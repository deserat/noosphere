/// View modes for the application
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ViewMode {
    /// List view - shows all items
    List,
    /// Detail view - shows a single item's details
    Detail,
    /// Capture view - quick capture input
    Capture,
    /// Search view - filter items
    Search,
    /// Settings view - application settings
    Settings,
}

/// Input modes for keyboard handling
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InputMode {
    /// Normal mode - navigation and commands
    Normal,
    /// Editing mode - text input
    Editing,
}

/// Minimal Item type (full implementation in future stories)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub id: String,
    pub title: String,
    pub category: String,
    pub created_at: String,
}

impl Item {
    /// Create a placeholder item for initial display
    pub fn placeholder() -> Self {
        Self {
            id: "1".to_string(),
            title: "Welcome to Noosphere".to_string(),
            category: "inbox".to_string(),
            created_at: "2024-01-01".to_string(),
        }
    }
}

/// Application state (Model in Elm Architecture)
pub struct App {
    /// Application running flag
    pub running: bool,
    /// Current view mode
    pub view_mode: ViewMode,
    /// Current input mode
    pub input_mode: InputMode,

    // List view state
    /// List of items to display
    pub items: Vec<Item>,
    /// Currently selected item index
    pub selected_index: usize,

    // Capture view state
    /// Text being entered in capture mode
    pub capture_input: String,
    /// Cursor position in capture input
    pub cursor_position: usize,

    // Search view state
    /// Search query filter
    pub search_query: String,

    // Status and messaging
    /// Status bar message
    pub status_message: Option<String>,
}

impl App {
    /// Create a new application instance with initial state
    pub fn new() -> Self {
        Self {
            running: true,
            view_mode: ViewMode::List,
            input_mode: InputMode::Normal,
            items: vec![Item::placeholder()],
            selected_index: 0,
            capture_input: String::new(),
            cursor_position: 0,
            search_query: String::new(),
            status_message: Some("Welcome! Press 'q' to quit, 'c' to capture, '/' to search".to_string()),
        }
    }

    /// Quit the application
    pub fn quit(&mut self) {
        self.running = false;
    }

    /// Move selection down in list view
    pub fn select_next(&mut self) {
        if !self.items.is_empty() {
            self.selected_index = (self.selected_index + 1) % self.items.len();
        }
    }

    /// Move selection up in list view
    pub fn select_previous(&mut self) {
        if !self.items.is_empty() {
            if self.selected_index == 0 {
                self.selected_index = self.items.len() - 1;
            } else {
                self.selected_index -= 1;
            }
        }
    }

    /// Get the currently selected item, if any
    pub fn selected_item(&self) -> Option<&Item> {
        self.items.get(self.selected_index)
    }

    /// Enter capture mode
    pub fn enter_capture_mode(&mut self) {
        self.view_mode = ViewMode::Capture;
        self.input_mode = InputMode::Editing;
        self.capture_input.clear();
        self.cursor_position = 0;
        self.status_message = Some("Capture mode: Type your note, press Enter to save, Esc to cancel".to_string());
    }

    /// Exit capture mode
    pub fn exit_capture_mode(&mut self) {
        self.view_mode = ViewMode::List;
        self.input_mode = InputMode::Normal;
        self.capture_input.clear();
        self.cursor_position = 0;
        self.status_message = Some("Capture cancelled".to_string());
    }

    /// Enter search mode
    pub fn enter_search_mode(&mut self) {
        self.view_mode = ViewMode::Search;
        self.input_mode = InputMode::Editing;
        self.search_query.clear();
        self.status_message = Some("Search mode: Type to filter, Esc to clear".to_string());
    }

    /// Exit search mode
    pub fn exit_search_mode(&mut self) {
        self.view_mode = ViewMode::List;
        self.input_mode = InputMode::Normal;
        self.search_query.clear();
        self.status_message = Some("Search cleared".to_string());
    }

    /// Enter detail view for the selected item
    pub fn enter_detail_view(&mut self) {
        if self.selected_item().is_some() {
            self.view_mode = ViewMode::Detail;
            self.status_message = Some("Detail view: Press Esc to return to list".to_string());
        }
    }

    /// Return to list view
    pub fn return_to_list(&mut self) {
        self.view_mode = ViewMode::List;
        self.input_mode = InputMode::Normal;
        self.status_message = None;
    }
}

impl Default for App {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_app_initialization() {
        let app = App::new();
        assert!(app.running);
        assert_eq!(app.view_mode, ViewMode::List);
        assert_eq!(app.input_mode, InputMode::Normal);
        assert_eq!(app.items.len(), 1);
        assert_eq!(app.selected_index, 0);
    }

    #[test]
    fn test_quit() {
        let mut app = App::new();
        assert!(app.running);
        app.quit();
        assert!(!app.running);
    }

    #[test]
    fn test_navigation() {
        let mut app = App::new();
        assert_eq!(app.selected_index, 0);

        app.select_next();
        assert_eq!(app.selected_index, 0); // Wraps around with 1 item

        app.select_previous();
        assert_eq!(app.selected_index, 0); // Wraps around with 1 item
    }

    #[test]
    fn test_capture_mode() {
        let mut app = App::new();
        assert_eq!(app.view_mode, ViewMode::List);
        assert_eq!(app.input_mode, InputMode::Normal);

        app.enter_capture_mode();
        assert_eq!(app.view_mode, ViewMode::Capture);
        assert_eq!(app.input_mode, InputMode::Editing);

        app.exit_capture_mode();
        assert_eq!(app.view_mode, ViewMode::List);
        assert_eq!(app.input_mode, InputMode::Normal);
    }
}
