# File Locking Mechanism for Concurrent Access

**Epic**: File Vault System
**Priority**: P2
**Story Points**: 5

## User Story

Implement a file locking mechanism to prevent corruption and data loss when the API service and external tools (like Obsidian) modify the same file concurrently.

## Acceptance Criteria

### Lock File Implementation
- [ ] `api-service/app/vault/lock.py` created with lock file context manager:
  ```python
  from contextlib import contextmanager
  import os
  import time
  from pathlib import Path

  @contextmanager
  def file_lock(file_path: str, timeout: int = 10):
      """
      Acquire file lock using .lock file pattern.

      Args:
          file_path: Path to file to lock
          timeout: Maximum seconds to wait for lock

      Raises:
          TimeoutError: If lock not acquired within timeout
      """
      lock_file = f"{file_path}.lock"
      acquired = False

      try:
          # Try to acquire lock
          start_time = time.time()
          while time.time() - start_time < timeout:
              try:
                  # Create lock file atomically
                  fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                  os.write(fd, f"{os.getpid()}".encode())
                  os.close(fd)
                  acquired = True
                  break
              except FileExistsError:
                  # Lock held by another process
                  time.sleep(0.1)

          if not acquired:
              raise TimeoutError(f"Could not acquire lock for {file_path}")

          yield  # Execute locked operation

      finally:
          # Release lock
          if acquired and os.path.exists(lock_file):
              os.unlink(lock_file)
  ```

### Stale Lock Handling
- [ ] Stale lock detection:
  ```python
  def is_stale_lock(lock_file: str, max_age: int = 300) -> bool:
      """Check if lock file is stale (older than max_age seconds)."""
      if not os.path.exists(lock_file):
          return False

      lock_age = time.time() - os.path.getmtime(lock_file)
      return lock_age > max_age

  def remove_stale_lock(lock_file: str) -> None:
      """Remove stale lock file."""
      if is_stale_lock(lock_file):
          os.unlink(lock_file)
          logging.warning(f"Removed stale lock: {lock_file}")
  ```
- [ ] Lock cleanup on process termination:
  ```python
  import atexit
  import signal

  _active_locks = set()

  def cleanup_locks():
      """Clean up all locks held by this process."""
      for lock_file in _active_locks:
          if os.exists(lock_file):
              os.unlink(lock_file)

  # Register cleanup handlers
  atexit.register(cleanup_locks)
  signal.signal(signal.SIGTERM, lambda s, f: cleanup_locks())
  signal.signal(signal.SIGINT, lambda s, f: cleanup_locks())
  ```

### Lock Usage Patterns
- [ ] File read (with lock):
  ```python
  def read_file_safely(file_path: str) -> str:
      """Read file with lock protection."""
      with file_lock(file_path):
          with open(file_path, 'r') as f:
              return f.read()
  ```
- [ ] File write (with lock):
  ```python
  def write_file_safely(file_path: str, content: str) -> None:
      """Write file with lock protection."""
      with file_lock(file_path):
          # Write to temp file first (atomic)
          temp_file = f"{file_path}.tmp"
          with open(temp_file, 'w') as f:
              f.write(content)
          os.replace(temp_file, file_path)
  ```
- [ ] Timeout handling:
  ```python
  try:
      with file_lock(file_path, timeout=5):
          # Perform file operation
          pass
  except TimeoutError:
      logger.error(f"Could not acquire lock for {file_path}")
      # Handle failure gracefully
  ```

### Integration with Vault Utilities
- [ ] Markdown writer uses locks:
  ```python
  # In api-service/app/vault/writer.py
  from .lock import file_lock

  def write_markdown_file_safe(
      file_path: str,
      metadata: Dict[str, Any],
      content: str
  ) -> None:
      """Write markdown file with lock protection."""
      with file_lock(file_path):
          write_markdown_file(file_path, metadata, content)
  ```
- [ ] Parser checks for locks before reading (optional, for safety):
  ```python
  def parse_markdown_file_safe(file_path: str) -> Dict[str, Any]:
      """Parse markdown file with lock protection."""
      with file_lock(file_path):
          return parse_markdown_file(file_path)
  ```

### Unit Tests
- [ ] Test suite created in `api-service/tests/vault/test_lock.py`:
  - Lock acquisition and release
  - Timeout behavior
  - Concurrent access (multiprocessing)
  - Stale lock detection
  - Lock cleanup on process termination
  - Edge cases (missing directories, permissions)
- [ ] All tests pass:
  ```bash
  pytest api-service/tests/vault/test_lock.py -v
  ```

## Technical Notes

**Lock File Pattern**:
- Simple, cross-platform approach
- Lock file: `{original_file}.lock`
- Contains process ID for debugging
- Atomic creation using O_CREAT | O_EXCL
- Removed when lock released

**Why Not flock()**:
- flock() behavior differs between filesystems (NFS issues)
- Lock files are more portable and visible
- Easier to debug (can see .lock files in filesystem)
- Works across network filesystems

**Stale Lock Recovery**:
- Locks older than 5 minutes are considered stale
- Automatic cleanup prevents permanent deadlocks
- Log warnings when removing stale locks
- Consider PID checking for more robust stale detection

**Race Conditions**:
- O_EXCL ensures atomic lock creation
- os.replace() ensures atomic file writes
- Lock acquired before any file operations
- Lock released in finally block

**Performance Impact**:
- Minimal (~1-2ms overhead per lock acquisition)
- Spinning with sleep(0.1) instead of busy wait
- Reasonable timeout defaults (5-10 seconds)

**External Tool Compatibility**:
- Obsidian doesn't use file locks (relies on atomic saves)
- This protects API service ↔ API service concurrency
- Still prevents corruption from rapid API + Obsidian edits
- User should avoid editing in both simultaneously

**Alternative Approaches Considered**:
1. **Database-based locking**: More complex, requires DB connection
2. **Redis-based locking**: Requires Redis dependency
3. **flock()**: Filesystem-dependent, NFS issues
4. **fcntl**: POSIX-only, not cross-platform
5. **File locks (chosen)**: Simple, portable, visible

## Dependencies

- **Blocks**:
  - EPIC-5-1 (API service will use locks for file operations)
- **Blocked By**:
  - EPIC-1-1 (Repository structure needed for src/vault directory)
  - EPIC-3-1 (Vault utilities needed to integrate locks)
- **Related**:
  - Phase 2 sync-service will respect these locks

## Verification

### Basic Lock Test
```bash
cd api-service
source venv/bin/activate

python -c "
from app.vault.lock import file_lock
import tempfile
import os

# Create test file
test_file = tempfile.mktemp()
with open(test_file, 'w') as f:
    f.write('test')

# Acquire lock
with file_lock(test_file):
    # Check lock file exists
    lock_file = f'{test_file}.lock'
    assert os.path.exists(lock_file), 'Lock file not created'

    # Verify lock file contains PID
    with open(lock_file, 'r') as f:
        pid = int(f.read())
    assert pid == os.getpid(), 'Lock file contains wrong PID'

# Check lock file removed after release
assert not os.path.exists(lock_file), 'Lock file not removed'

os.unlink(test_file)
print('✓ Basic lock test passed')
"
```

### Timeout Test
```bash
python -c "
from app.vault.lock import file_lock
import tempfile
import os

test_file = tempfile.mktemp()
with open(test_file, 'w') as f:
    f.write('test')

# Acquire lock
with file_lock(test_file):
    # Try to acquire again (should timeout)
    try:
        with file_lock(test_file, timeout=1):
            assert False, 'Should not acquire lock'
    except TimeoutError:
        print('✓ Timeout test passed')

os.unlink(test_file)
"
```

### Concurrent Access Test
```bash
python -c "
from app.vault.lock import file_lock
import tempfile
import multiprocessing
import time

def worker(file_path, worker_id):
    \"\"\"Worker process that tries to acquire lock.\"\"\"
    try:
        with file_lock(file_path, timeout=5):
            # Simulate work
            time.sleep(0.5)
            print(f'Worker {worker_id} acquired lock')
    except TimeoutError:
        print(f'Worker {worker_id} timeout')

# Create test file
test_file = tempfile.mktemp()
with open(test_file, 'w') as f:
    f.write('test')

# Start multiple workers
processes = []
for i in range(3):
    p = multiprocessing.Process(target=worker, args=(test_file, i))
    p.start()
    processes.append(p)

# Wait for all workers
for p in processes:
    p.join()

import os
os.unlink(test_file)
print('✓ Concurrent access test passed (all workers ran)')
"
```

### Stale Lock Test
```bash
python -c "
from app.vault.lock import is_stale_lock, remove_stale_lock
import tempfile
import time
import os

test_file = tempfile.mktemp()
lock_file = f'{test_file}.lock'

# Create old lock file
with open(lock_file, 'w') as f:
    f.write('12345')

# Make it old (modify timestamp)
old_time = time.time() - 400  # 400 seconds ago
os.utime(lock_file, (old_time, old_time))

# Check stale detection
assert is_stale_lock(lock_file, max_age=300), 'Lock should be stale'

# Remove stale lock
remove_stale_lock(lock_file)
assert not os.path.exists(lock_file), 'Stale lock not removed'

print('✓ Stale lock test passed')
"
```

### Integration Test with Writer
```bash
python -c "
from app.vault.writer import write_markdown_file_safe
from app.vault.parser import parse_markdown_file
import tempfile
import os

test_file = tempfile.mktemp(suffix='.md')

# Write file safely (with lock)
metadata = {'title': 'Lock Test', 'category': 'Ideas'}
content = '# Lock Test\n\nThis is protected content.'

write_markdown_file_safe(test_file, metadata, content)

# Verify file written
assert os.path.exists(test_file)

# Verify lock was released
lock_file = f'{test_file}.lock'
assert not os.path.exists(lock_file), 'Lock not released after write'

# Verify content
data = parse_markdown_file(test_file)
assert data['metadata']['title'] == 'Lock Test'

os.unlink(test_file)
print('✓ Integration test passed')
"
```

### Unit Test Suite
```bash
cd api-service
pytest tests/vault/test_lock.py -v

# Expected output:
# tests/vault/test_lock.py::test_lock_acquire_release PASSED
# tests/vault/test_lock.py::test_lock_timeout PASSED
# tests/vault/test_lock.py::test_concurrent_access PASSED
# tests/vault/test_lock.py::test_stale_lock_detection PASSED
# tests/vault/test_lock.py::test_stale_lock_removal PASSED
# tests/vault/test_lock.py::test_lock_cleanup_on_exit PASSED
#
# ======== 6 passed in 2.5s ========
```

**Completion Criteria**:
- [ ] Lock file context manager implemented
- [ ] Locks acquired and released correctly
- [ ] Timeout handling works (raises TimeoutError)
- [ ] Stale lock detection and removal works
- [ ] Lock cleanup on process termination registered
- [ ] Integration with vault writer and parser complete
- [ ] All unit tests pass
- [ ] Concurrent access prevented (only one process can lock at a time)
- [ ] Documentation explains lock mechanism and usage patterns
- [ ] Lock files visible in filesystem for debugging
