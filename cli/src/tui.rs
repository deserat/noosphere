use crossterm::{
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{backend::CrosstermBackend, Terminal};
use std::{
    io::{self, Stdout},
    panic,
};

/// Type alias for the terminal with crossterm backend
pub type Tui = Terminal<CrosstermBackend<Stdout>>;

/// Initialize the terminal for TUI mode
///
/// This function:
/// - Installs a panic hook to restore the terminal on panic
/// - Enables raw mode (bypasses line buffering)
/// - Enters alternate screen (preserves terminal history)
/// - Creates and returns a Terminal instance
pub fn init() -> io::Result<Tui> {
    // Install panic hook for clean terminal restoration
    install_panic_hook();

    // Enable raw mode for immediate key event processing
    enable_raw_mode()?;

    // Enter alternate screen to preserve terminal history
    execute!(io::stdout(), EnterAlternateScreen)?;

    // Create terminal with crossterm backend
    let backend = CrosstermBackend::new(io::stdout());
    let terminal = Terminal::new(backend)?;

    Ok(terminal)
}

/// Restore the terminal to its original state
///
/// This function:
/// - Disables raw mode
/// - Leaves alternate screen
///
/// Should be called before the application exits.
pub fn restore() -> io::Result<()> {
    // Disable raw mode
    disable_raw_mode()?;

    // Leave alternate screen and restore cursor
    execute!(io::stdout(), LeaveAlternateScreen)?;

    Ok(())
}

/// Install a panic hook that restores the terminal before panicking
///
/// This ensures that if the application panics, the terminal is properly
/// restored so the panic message is visible and the terminal is usable.
fn install_panic_hook() {
    let original_hook = panic::take_hook();

    panic::set_hook(Box::new(move |panic_info| {
        // Try to restore the terminal (ignore errors as we're panicking anyway)
        let _ = restore();

        // Call the original panic hook to print the panic message
        original_hook(panic_info);
    }));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_panic_hook_installed() {
        // This test just ensures the panic hook installation doesn't panic itself
        install_panic_hook();
        // If we got here, the hook was installed successfully
    }

    // Note: We can't easily test init() and restore() in unit tests as they
    // modify the actual terminal. These should be tested manually or with
    // integration tests.
}
