use crate::app::{App, InputMode, ViewMode};
use crate::event::Event;
use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

/// Main event handler (Update in Elm Architecture)
///
/// Routes events to appropriate handlers based on event type.
pub fn handle_event(app: &mut App, event: Event) -> Result<(), Box<dyn std::error::Error>> {
    match event {
        Event::Key(key_event) => handle_key_event(app, key_event),
        Event::Mouse(_) => Ok(()), // Mouse events not handled in minimal version
        Event::Resize(_, _) => Ok(()), // Resize handled automatically by ratatui
        Event::Tick => Ok(()), // Tick events used for periodic updates (none needed yet)
    }
}

/// Handle keyboard events
///
/// Routes to input mode-specific handlers.
fn handle_key_event(app: &mut App, key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    match app.input_mode {
        InputMode::Normal => handle_normal_mode(app, key),
        InputMode::Editing => handle_editing_mode(app, key),
    }
}

/// Handle keys in normal mode (navigation and commands)
fn handle_normal_mode(app: &mut App, key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    // Global keybindings (work in all view modes)
    match (key.code, key.modifiers) {
        // Quit
        (KeyCode::Char('q'), KeyModifiers::NONE) => {
            app.quit();
            return Ok(());
        }
        (KeyCode::Char('c'), KeyModifiers::CONTROL) => {
            app.quit();
            return Ok(());
        }

        // Enter capture mode
        (KeyCode::Char('c'), KeyModifiers::NONE) => {
            app.enter_capture_mode();
            return Ok(());
        }

        // Enter search mode
        (KeyCode::Char('/'), KeyModifiers::NONE) => {
            app.enter_search_mode();
            return Ok(());
        }

        // Help (not implemented yet)
        (KeyCode::Char('?'), KeyModifiers::NONE) => {
            app.status_message = Some("Help: q=quit c=capture /=search ↑↓=navigate Enter=detail".to_string());
            return Ok(());
        }

        _ => {}
    }

    // View-specific keybindings
    handle_view_specific_keys(app, key)
}

/// Handle view-specific keys
fn handle_view_specific_keys(
    app: &mut App,
    key: KeyEvent,
) -> Result<(), Box<dyn std::error::Error>> {
    match app.view_mode {
        ViewMode::List => handle_list_keys(app, key),
        ViewMode::Detail => handle_detail_keys(app, key),
        ViewMode::Capture => handle_capture_keys(app, key),
        ViewMode::Search => handle_search_keys(app, key),
        ViewMode::Settings => handle_settings_keys(app, key),
    }
}

/// Handle keys in list view
fn handle_list_keys(app: &mut App, key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    match key.code {
        // Navigation - j/k (vim-style)
        KeyCode::Char('j') => app.select_next(),
        KeyCode::Char('k') => app.select_previous(),

        // Navigation - arrow keys
        KeyCode::Down => app.select_next(),
        KeyCode::Up => app.select_previous(),

        // Enter detail view
        KeyCode::Enter => app.enter_detail_view(),

        // Triage mode (not implemented yet)
        KeyCode::Char('t') => {
            app.status_message = Some("Triage mode not implemented yet".to_string());
        }

        _ => {}
    }

    Ok(())
}

/// Handle keys in detail view
fn handle_detail_keys(app: &mut App, key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    match key.code {
        // Return to list
        KeyCode::Esc => app.return_to_list(),

        // Edit (not implemented yet)
        KeyCode::Char('e') => {
            app.status_message = Some("Edit mode not implemented yet".to_string());
        }

        // Delete (not implemented yet)
        KeyCode::Char('d') => {
            app.status_message = Some("Delete not implemented yet".to_string());
        }

        _ => {}
    }

    Ok(())
}

/// Handle keys in capture view (should use editing mode handlers)
fn handle_capture_keys(_app: &mut App, _key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    // Capture view uses editing mode, so this shouldn't be called
    // But we include it for completeness
    Ok(())
}

/// Handle keys in search view (should use editing mode handlers)
fn handle_search_keys(_app: &mut App, _key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    // Search view uses editing mode, so this shouldn't be called
    // But we include it for completeness
    Ok(())
}

/// Handle keys in settings view
fn handle_settings_keys(app: &mut App, key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    match key.code {
        // Return to list
        KeyCode::Esc => app.return_to_list(),

        _ => {}
    }

    Ok(())
}

/// Handle keys in editing mode (text input)
fn handle_editing_mode(app: &mut App, key: KeyEvent) -> Result<(), Box<dyn std::error::Error>> {
    match key.code {
        // Exit editing mode
        KeyCode::Esc => {
            match app.view_mode {
                ViewMode::Capture => app.exit_capture_mode(),
                ViewMode::Search => app.exit_search_mode(),
                _ => {
                    app.input_mode = InputMode::Normal;
                }
            }
        }

        // Submit input
        KeyCode::Enter => {
            match app.view_mode {
                ViewMode::Capture => {
                    // In future stories, this will save the capture
                    app.status_message = Some(format!(
                        "Captured: {} (save not implemented yet)",
                        app.capture_input
                    ));
                    app.exit_capture_mode();
                }
                ViewMode::Search => {
                    // Search is live-filtered, Enter just confirms
                    app.input_mode = InputMode::Normal;
                }
                _ => {}
            }
        }

        // Character input
        KeyCode::Char(c) => {
            match app.view_mode {
                ViewMode::Capture => {
                    app.capture_input.insert(app.cursor_position, c);
                    app.cursor_position += 1;
                }
                ViewMode::Search => {
                    app.search_query.push(c);
                }
                _ => {}
            }
        }

        // Backspace
        KeyCode::Backspace => {
            match app.view_mode {
                ViewMode::Capture => {
                    if app.cursor_position > 0 {
                        app.cursor_position -= 1;
                        app.capture_input.remove(app.cursor_position);
                    }
                }
                ViewMode::Search => {
                    app.search_query.pop();
                }
                _ => {}
            }
        }

        // Delete
        KeyCode::Delete => {
            match app.view_mode {
                ViewMode::Capture => {
                    if app.cursor_position < app.capture_input.len() {
                        app.capture_input.remove(app.cursor_position);
                    }
                }
                _ => {}
            }
        }

        // Cursor movement (left/right)
        KeyCode::Left => {
            if app.view_mode == ViewMode::Capture && app.cursor_position > 0 {
                app.cursor_position -= 1;
            }
        }
        KeyCode::Right => {
            if app.view_mode == ViewMode::Capture
                && app.cursor_position < app.capture_input.len()
            {
                app.cursor_position += 1;
            }
        }

        // Home/End
        KeyCode::Home => {
            if app.view_mode == ViewMode::Capture {
                app.cursor_position = 0;
            }
        }
        KeyCode::End => {
            if app.view_mode == ViewMode::Capture {
                app.cursor_position = app.capture_input.len();
            }
        }

        _ => {}
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crossterm::event::KeyCode;

    #[test]
    fn test_quit_keys() {
        let mut app = App::new();
        assert!(app.running);

        // Test 'q' key
        let key = KeyEvent::new(KeyCode::Char('q'), KeyModifiers::NONE);
        handle_key_event(&mut app, key).unwrap();
        assert!(!app.running);

        // Test Ctrl+C
        let mut app = App::new();
        let key = KeyEvent::new(KeyCode::Char('c'), KeyModifiers::CONTROL);
        handle_key_event(&mut app, key).unwrap();
        assert!(!app.running);
    }

    #[test]
    fn test_capture_mode_activation() {
        let mut app = App::new();
        assert_eq!(app.view_mode, ViewMode::List);
        assert_eq!(app.input_mode, InputMode::Normal);

        // Press 'c' to enter capture mode
        let key = KeyEvent::new(KeyCode::Char('c'), KeyModifiers::NONE);
        handle_key_event(&mut app, key).unwrap();

        assert_eq!(app.view_mode, ViewMode::Capture);
        assert_eq!(app.input_mode, InputMode::Editing);
    }

    #[test]
    fn test_navigation() {
        let mut app = App::new();
        let initial_index = app.selected_index;

        // Press 'j' to move down
        let key = KeyEvent::new(KeyCode::Char('j'), KeyModifiers::NONE);
        handle_key_event(&mut app, key).unwrap();

        // With one item, should wrap back to 0
        assert_eq!(app.selected_index, initial_index);

        // Press 'k' to move up
        let key = KeyEvent::new(KeyCode::Char('k'), KeyModifiers::NONE);
        handle_key_event(&mut app, key).unwrap();

        assert_eq!(app.selected_index, initial_index);
    }

    #[test]
    fn test_text_input_in_capture() {
        let mut app = App::new();
        app.enter_capture_mode();

        // Type 'test'
        for c in "test".chars() {
            let key = KeyEvent::new(KeyCode::Char(c), KeyModifiers::NONE);
            handle_key_event(&mut app, key).unwrap();
        }

        assert_eq!(app.capture_input, "test");
        assert_eq!(app.cursor_position, 4);
    }

    #[test]
    fn test_backspace_in_capture() {
        let mut app = App::new();
        app.enter_capture_mode();

        // Type 'test'
        for c in "test".chars() {
            let key = KeyEvent::new(KeyCode::Char(c), KeyModifiers::NONE);
            handle_key_event(&mut app, key).unwrap();
        }

        // Backspace once
        let key = KeyEvent::new(KeyCode::Backspace, KeyModifiers::NONE);
        handle_key_event(&mut app, key).unwrap();

        assert_eq!(app.capture_input, "tes");
        assert_eq!(app.cursor_position, 3);
    }
}
