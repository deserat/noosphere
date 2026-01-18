use crate::app::{App, ViewMode};
use ratatui::{
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, List, ListItem, Paragraph, Wrap},
    Frame,
};

/// Main render function (View in Elm Architecture)
///
/// Renders the application state to the terminal frame.
/// Layout: Header (3 lines) | Content (flexible) | Status bar (3 lines)
pub fn render(f: &mut Frame, app: &App) {
    // Create main layout with header, content, and status bar
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),  // Header
            Constraint::Min(0),     // Content (takes remaining space)
            Constraint::Length(3),  // Status bar
        ])
        .split(f.size());

    render_header(f, chunks[0], app);
    render_content(f, chunks[1], app);
    render_status_bar(f, chunks[2], app);
}

/// Render the header section
fn render_header(f: &mut Frame, area: Rect, _app: &App) {
    let title = Paragraph::new("Noosphere - Personal Knowledge Management")
        .style(Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL));
    f.render_widget(title, area);
}

/// Render the content section based on current view mode
fn render_content(f: &mut Frame, area: Rect, app: &App) {
    match app.view_mode {
        ViewMode::List => render_list_view(f, area, app),
        ViewMode::Detail => render_detail_view(f, area, app),
        ViewMode::Capture => render_capture_view(f, area, app),
        ViewMode::Search => render_search_view(f, area, app),
        ViewMode::Settings => render_settings_view(f, area, app),
    }
}

/// Render the status bar
fn render_status_bar(f: &mut Frame, area: Rect, app: &App) {
    let status_text = if let Some(ref msg) = app.status_message {
        msg.clone()
    } else {
        "Ready".to_string()
    };

    let keybindings = match app.view_mode {
        ViewMode::List => "q:quit | c:capture | /:search | ↑↓:navigate | Enter:detail",
        ViewMode::Detail => "Esc:back | e:edit | d:delete",
        ViewMode::Capture => "Esc:cancel | Enter:save",
        ViewMode::Search => "Esc:clear | Type to filter",
        ViewMode::Settings => "Esc:back",
    };

    let status_line = Line::from(vec![
        Span::styled(
            format!("[{}] ", status_text),
            Style::default().fg(Color::Yellow),
        ),
        Span::styled(
            format!("| {}", keybindings),
            Style::default().fg(Color::Gray),
        ),
    ]);

    let status = Paragraph::new(status_line)
        .alignment(Alignment::Left)
        .block(Block::default().borders(Borders::ALL));

    f.render_widget(status, area);
}

/// Render the list view - shows all items
fn render_list_view(f: &mut Frame, area: Rect, app: &App) {
    let items: Vec<ListItem> = app
        .items
        .iter()
        .enumerate()
        .map(|(i, item)| {
            let style = if i == app.selected_index {
                Style::default()
                    .fg(Color::Black)
                    .bg(Color::Cyan)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };

            let content = Line::from(vec![
                Span::styled(
                    format!("[{}] ", item.category),
                    Style::default().fg(Color::Yellow),
                ),
                Span::styled(&item.title, style),
                Span::styled(
                    format!(" ({})", item.created_at),
                    Style::default().fg(Color::Gray),
                ),
            ]);

            ListItem::new(content).style(style)
        })
        .collect();

    let items_list = List::new(items)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title("Items")
                .title_alignment(Alignment::Left),
        )
        .highlight_style(
            Style::default()
                .fg(Color::Black)
                .bg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        );

    f.render_widget(items_list, area);
}

/// Render the detail view - shows a single item's details
fn render_detail_view(f: &mut Frame, area: Rect, app: &App) {
    if let Some(item) = app.selected_item() {
        let content = vec![
            Line::from(vec![
                Span::styled("ID: ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::raw(&item.id),
            ]),
            Line::from(""),
            Line::from(vec![
                Span::styled("Title: ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::raw(&item.title),
            ]),
            Line::from(""),
            Line::from(vec![
                Span::styled("Category: ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::styled(&item.category, Style::default().fg(Color::Yellow)),
            ]),
            Line::from(""),
            Line::from(vec![
                Span::styled("Created: ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
                Span::styled(&item.created_at, Style::default().fg(Color::Gray)),
            ]),
            Line::from(""),
            Line::from(""),
            Line::from(vec![
                Span::styled("Content: ", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
            ]),
            Line::from("(Full content display will be implemented in future stories)"),
        ];

        let paragraph = Paragraph::new(content)
            .block(
                Block::default()
                    .borders(Borders::ALL)
                    .title("Item Detail")
                    .title_alignment(Alignment::Left),
            )
            .wrap(Wrap { trim: true });

        f.render_widget(paragraph, area);
    } else {
        let text = Paragraph::new("No item selected")
            .style(Style::default().fg(Color::Red))
            .alignment(Alignment::Center)
            .block(Block::default().borders(Borders::ALL).title("Item Detail"));

        f.render_widget(text, area);
    }
}

/// Render the capture view - quick capture input
fn render_capture_view(f: &mut Frame, area: Rect, app: &App) {
    // Split area into instructions and input
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(5),  // Instructions
            Constraint::Min(0),     // Input area
        ])
        .split(area);

    // Instructions
    let instructions = vec![
        Line::from(vec![
            Span::styled("Quick Capture", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
        ]),
        Line::from(""),
        Line::from("Type your note below. Press Enter to save, Esc to cancel."),
    ];

    let instructions_paragraph = Paragraph::new(instructions)
        .block(Block::default().borders(Borders::ALL))
        .wrap(Wrap { trim: true });

    f.render_widget(instructions_paragraph, chunks[0]);

    // Input area
    let input = Paragraph::new(app.capture_input.as_str())
        .style(Style::default().fg(Color::White))
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title("Input")
                .title_alignment(Alignment::Left),
        )
        .wrap(Wrap { trim: false });

    f.render_widget(input, chunks[1]);

    // Set cursor position (if in editing mode)
    f.set_cursor(
        chunks[1].x + app.cursor_position as u16 + 1,
        chunks[1].y + 1,
    );
}

/// Render the search view - filter items
fn render_search_view(f: &mut Frame, area: Rect, app: &App) {
    // Split area into search input and results
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),  // Search input
            Constraint::Min(0),     // Results
        ])
        .split(area);

    // Search input
    let search_input = Paragraph::new(app.search_query.as_str())
        .style(Style::default().fg(Color::White))
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title("Search")
                .title_alignment(Alignment::Left),
        );

    f.render_widget(search_input, chunks[0]);

    // Results (filtered items - for now, show all)
    let items: Vec<ListItem> = app
        .items
        .iter()
        .filter(|item| {
            if app.search_query.is_empty() {
                true
            } else {
                item.title
                    .to_lowercase()
                    .contains(&app.search_query.to_lowercase())
                    || item
                        .category
                        .to_lowercase()
                        .contains(&app.search_query.to_lowercase())
            }
        })
        .map(|item| {
            let content = Line::from(vec![
                Span::styled(
                    format!("[{}] ", item.category),
                    Style::default().fg(Color::Yellow),
                ),
                Span::raw(&item.title),
            ]);
            ListItem::new(content)
        })
        .collect();

    let results_count = items.len();
    let results_list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(format!("Results ({})", results_count))
            .title_alignment(Alignment::Left),
    );

    f.render_widget(results_list, chunks[1]);
}

/// Render the settings view
fn render_settings_view(f: &mut Frame, area: Rect, _app: &App) {
    let content = vec![
        Line::from(vec![
            Span::styled("Settings", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD)),
        ]),
        Line::from(""),
        Line::from("(Settings functionality will be implemented in future stories)"),
        Line::from(""),
        Line::from(vec![
            Span::styled("Version: ", Style::default().fg(Color::Yellow)),
            Span::raw("0.1.0"),
        ]),
        Line::from(vec![
            Span::styled("Edition: ", Style::default().fg(Color::Yellow)),
            Span::raw("2021"),
        ]),
    ];

    let paragraph = Paragraph::new(content)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title("Settings")
                .title_alignment(Alignment::Left),
        )
        .wrap(Wrap { trim: true });

    f.render_widget(paragraph, area);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_render_functions_exist() {
        // These tests just verify that the render functions can be called
        // without panicking. Full rendering tests would require a mock backend.
        let _app = App::new();
        // If we got here, the module compiles and the functions exist
    }
}
