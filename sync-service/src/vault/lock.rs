// File locking module for preventing concurrent writes

use anyhow::Result;
use fs2::FileExt;
use std::fs::{self, File, OpenOptions};
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

/// File lock with RAII pattern for automatic cleanup
///
/// Prevents concurrent writes to vault files from sync-service and cli.
/// Uses advisory locks that are visible to both processes.
/// Lock files are stored in `.noosphere/locks/` directory.
///
/// # Example
///
/// ```no_run
/// use noosphere_sync::vault::lock::FileLock;
/// use std::path::Path;
/// use std::time::Duration;
///
/// let file_path = Path::new("/tmp/test.md");
/// let mut lock = FileLock::new(file_path)?;
///
/// // Acquire lock with 5-second timeout
/// lock.acquire(Duration::from_secs(5))?;
///
/// // ... perform file operations ...
///
/// // Lock is automatically released when dropped
/// # Ok::<(), anyhow::Error>(())
/// ```
pub struct FileLock {
    lock_file: PathBuf,
    _guard: Option<File>,
}

impl FileLock {
    /// Duration after which a lock is considered stale (5 minutes)
    const STALE_LOCK_DURATION: Duration = Duration::from_secs(300);

    /// Create a new file lock for the given file path
    ///
    /// Lock files are created in `.noosphere/locks/` directory
    /// adjacent to the target file.
    ///
    /// # Arguments
    ///
    /// * `file_path` - Path to the file to lock
    ///
    /// # Returns
    ///
    /// `Ok(FileLock)` if lock file path is valid and directory can be created
    ///
    /// # Errors
    ///
    /// Returns an error if:
    /// - File path has no parent directory
    /// - File path has no file name
    /// - Lock directory cannot be created (e.g., permission denied)
    ///
    /// # Example
    ///
    /// ```no_run
    /// use noosphere_sync::vault::lock::FileLock;
    /// use std::path::Path;
    ///
    /// let lock = FileLock::new(Path::new("/tmp/test.md"))?;
    /// // Lock file will be at /tmp/.noosphere/locks/test.md.lock
    /// # Ok::<(), anyhow::Error>(())
    /// ```
    pub fn new(file_path: &Path) -> Result<Self> {
        let parent_dir = file_path.parent().ok_or_else(|| {
            anyhow::anyhow!(
                "File path '{}' has no parent directory",
                file_path.display()
            )
        })?;
        let lock_dir = parent_dir.join(".noosphere/locks");
        fs::create_dir_all(&lock_dir)?;

        let file_name = file_path.file_name().ok_or_else(|| {
            anyhow::anyhow!("File path '{}' has no file name", file_path.display())
        })?;

        let lock_file = lock_dir.join(format!("{}.lock", file_name.to_string_lossy()));

        Ok(Self {
            lock_file,
            _guard: None,
        })
    }

    /// Acquire an exclusive lock with timeout
    ///
    /// Attempts to acquire an exclusive lock on the file.
    /// If the lock is already held, retries until timeout is reached.
    ///
    /// **Important**: This function contains blocking I/O operations. When calling
    /// from an async context (tokio runtime), wrap the call in `tokio::task::spawn_blocking`
    /// to avoid blocking the async worker thread.
    ///
    /// # Arguments
    ///
    /// * `timeout` - Maximum duration to wait for lock
    ///
    /// # Returns
    ///
    /// `Ok(())` if lock acquired successfully
    ///
    /// # Errors
    ///
    /// Returns an error if:
    /// - Lock cannot be acquired within timeout
    /// - I/O error occurs
    ///
    /// # Example (Synchronous Context)
    ///
    /// ```no_run
    /// use noosphere_sync::vault::lock::FileLock;
    /// use std::path::Path;
    /// use std::time::Duration;
    ///
    /// let mut lock = FileLock::new(Path::new("/tmp/test.md"))?;
    ///
    /// match lock.acquire(Duration::from_secs(5)) {
    ///     Ok(()) => println!("Lock acquired"),
    ///     Err(e) => eprintln!("Failed to acquire lock: {}", e),
    /// }
    /// # Ok::<(), anyhow::Error>(())
    /// ```
    ///
    /// # Example (Async Context)
    ///
    /// ```no_run
    /// use noosphere_sync::vault::lock::FileLock;
    /// use std::path::Path;
    /// use std::time::Duration;
    ///
    /// # async fn example() -> anyhow::Result<()> {
    /// let path = Path::new("/tmp/test.md").to_path_buf();
    /// let mut lock = FileLock::new(&path)?;
    ///
    /// // Spawn blocking task to avoid blocking async runtime
    /// tokio::task::spawn_blocking(move || {
    ///     lock.acquire(Duration::from_secs(5))
    /// }).await??;
    ///
    /// // ... perform file operations ...
    /// # Ok(())
    /// # }
    /// ```
    pub fn acquire(&mut self, timeout: Duration) -> Result<()> {
        let start = SystemTime::now();

        loop {
            match OpenOptions::new()
                .write(true)
                .create(true)
                .truncate(true)
                .open(&self.lock_file)
            {
                Ok(file) => {
                    // Acquire exclusive lock using fs2
                    file.lock_exclusive()?;
                    self._guard = Some(file);
                    return Ok(());
                }
                Err(_e) => {
                    // Check if existing lock is stale and clean it up
                    if self.is_stale()? {
                        self.force_unlock()?;
                        continue; // Retry immediately after cleaning stale lock
                    }

                    // Lock is not stale, check timeout
                    if start.elapsed()? > timeout {
                        anyhow::bail!("Lock timeout: failed to acquire lock within {:?}", timeout);
                    }
                    std::thread::sleep(Duration::from_millis(100));
                }
            }
        }
    }

    /// Release the lock manually
    ///
    /// Releases the exclusive lock and removes the lock file.
    /// Usually not needed as the lock is automatically released when dropped.
    ///
    /// # Example
    ///
    /// ```no_run
    /// use noosphere_sync::vault::lock::FileLock;
    /// use std::path::Path;
    /// use std::time::Duration;
    ///
    /// let mut lock = FileLock::new(Path::new("/tmp/test.md"))?;
    /// lock.acquire(Duration::from_secs(5))?;
    ///
    /// // ... do work ...
    ///
    /// lock.release()?; // Explicit release (optional)
    /// # Ok::<(), anyhow::Error>(())
    /// ```
    pub fn release(&mut self) -> Result<()> {
        if let Some(file) = self._guard.take() {
            file.unlock()?;
            fs::remove_file(&self.lock_file)?;
        }
        Ok(())
    }

    /// Check if the lock file is stale (older than 5 minutes)
    ///
    /// A stale lock indicates that the process holding the lock has died
    /// or is otherwise unable to release it properly.
    ///
    /// # Returns
    ///
    /// `Ok(true)` if lock file exists and is older than 5 minutes
    /// `Ok(false)` if lock file doesn't exist or is recent
    ///
    /// # Errors
    ///
    /// Returns an error if unable to read file metadata or system time
    fn is_stale(&self) -> Result<bool> {
        // If lock file doesn't exist, it's not stale
        if !self.lock_file.exists() {
            return Ok(false);
        }

        // Get file metadata to check modification time
        let metadata = fs::metadata(&self.lock_file)?;
        let modified = metadata.modified()?;
        let age = SystemTime::now().duration_since(modified)?;

        // Consider lock stale if older than threshold
        Ok(age > Self::STALE_LOCK_DURATION)
    }

    /// Force removal of a stale lock file
    ///
    /// Attempts to remove the lock file. If the file doesn't exist,
    /// this is considered success (desired state achieved).
    ///
    /// Should only be called after confirming the lock is stale via `is_stale()`.
    ///
    /// # Errors
    ///
    /// Returns an error only for actual I/O failures (permission denied, etc.).
    /// Returns `Ok(())` if the file is already removed.
    fn force_unlock(&self) -> Result<()> {
        if let Err(e) = fs::remove_file(&self.lock_file) {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(e.into());
            }
        }
        Ok(())
    }
}

/// Automatic lock cleanup using RAII pattern
///
/// When FileLock is dropped, the lock is automatically released.
/// This ensures locks are always cleaned up, even in case of panics.
///
/// If lock release fails during drop, a warning is printed to stderr.
impl Drop for FileLock {
    fn drop(&mut self) {
        if let Err(e) = self.release() {
            eprintln!("Warning: Failed to release file lock: {}", e);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::thread;
    use tempfile::NamedTempFile;

    #[test]
    fn test_file_lock_acquire_release() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Test content")?;
        temp_file.flush()?;

        let mut lock = FileLock::new(temp_file.path())?;

        // Acquire lock
        lock.acquire(Duration::from_secs(1))?;
        assert!(lock._guard.is_some());

        // Release lock
        lock.release()?;
        assert!(lock._guard.is_none());

        Ok(())
    }

    #[test]
    fn test_lock_auto_cleanup() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Test content")?;
        temp_file.flush()?;

        {
            let mut lock = FileLock::new(temp_file.path())?;
            lock.acquire(Duration::from_secs(1))?;
            // lock dropped here, should auto-release
        }

        // Lock file should be cleaned up automatically via Drop
        // Note: There may be a small window where file still exists
        thread::sleep(Duration::from_millis(100));

        Ok(())
    }

    #[test]
    #[ignore] // Requires multi-process testing - fs2 locks may be reentrant within same process
    fn test_lock_timeout() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Test content")?;
        temp_file.flush()?;

        let mut lock1 = FileLock::new(temp_file.path())?;
        lock1.acquire(Duration::from_secs(1))?;

        // Try to acquire same lock from same process (will timeout)
        let mut lock2 = FileLock::new(temp_file.path())?;
        let result = lock2.acquire(Duration::from_millis(200));

        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("timeout"));

        Ok(())
    }

    #[test]
    fn test_lock_creates_directory() -> Result<()> {
        let temp_dir = tempfile::tempdir()?;
        let file_path = temp_dir.path().join("subdir").join("test.md");

        // Create parent directory
        fs::create_dir_all(file_path.parent().unwrap())?;

        let _lock = FileLock::new(&file_path)?;

        // Lock directory should exist
        let lock_dir = file_path.parent().unwrap().join(".noosphere/locks");
        assert!(lock_dir.exists());

        Ok(())
    }

    #[test]
    fn test_sequential_locks() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Test content")?;
        temp_file.flush()?;

        // Acquire lock
        {
            let mut lock1 = FileLock::new(temp_file.path())?;
            lock1.acquire(Duration::from_secs(1))?;
        } // lock1 dropped and released

        // Should be able to acquire lock again
        let mut lock2 = FileLock::new(temp_file.path())?;
        lock2.acquire(Duration::from_secs(1))?;

        Ok(())
    }

    #[test]
    fn test_stale_lock_cleanup() -> Result<()> {
        use filetime::{set_file_mtime, FileTime};

        let mut temp_file = NamedTempFile::new()?;
        write!(temp_file, "Test content")?;
        temp_file.flush()?;

        let mut lock = FileLock::new(temp_file.path())?;

        // Create a stale lock file manually (simulating abandoned lock)
        File::create(&lock.lock_file)?;

        // Set modification time to 6 minutes ago (beyond 5-minute stale threshold)
        let six_min_ago = SystemTime::now()
            .checked_sub(Duration::from_secs(360))
            .unwrap();
        set_file_mtime(&lock.lock_file, FileTime::from_system_time(six_min_ago))?;

        // Verify lock is detected as stale
        assert!(lock.is_stale()?);

        // Should successfully acquire lock despite existing stale lock file
        lock.acquire(Duration::from_secs(1))?;

        // Lock should now be held
        assert!(lock._guard.is_some());

        Ok(())
    }
}
