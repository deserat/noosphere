// Module declarations
mod app;
mod event;
mod handler;
mod tui;
mod ui;

// Placeholder modules (implemented in future stories)
mod api;
mod components;

use app::App;
use event::{Event, EventHandler};
use handler::handle_event;
use std::time::Duration;

/// Application entry point
///
/// Implements the Elm Architecture event loop:
/// 1. Initialize state (App::new)
/// 2. Initialize terminal
/// 3. Event Loop:
///    - Render current state (ui::render) [View]
///    - Poll for next event (event_handler.next)
///    - Update state (handle_event) [Update]
///    - Repeat while running
/// 4. Cleanup terminal
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing/logging
    // Set RUST_LOG environment variable to control log levels
    // Example: RUST_LOG=debug cargo run
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info")),
        )
        .init();

    tracing::info!("Starting Noosphere CLI");

    // Initialize terminal for TUI mode
    let mut terminal = tui::init()?;
    tracing::info!("Terminal initialized");

    // Create application state (Model in Elm Architecture)
    let mut app = App::new();
    tracing::info!("Application state initialized");

    // Create event handler with 100ms tick rate
    let mut event_handler = EventHandler::new(Duration::from_millis(100));
    tracing::debug!("Event handler created with 100ms tick rate");

    // Main event loop: Poll → Update → Render
    // This is the core of the Elm Architecture pattern
    while app.running {
        // RENDER: Draw current state to terminal (View in Elm)
        terminal.draw(|f| ui::render(f, &app))?;

        // POLL: Wait for next event (keyboard, mouse, tick)
        let event = event_handler.next()?;

        // Log significant events (not ticks)
        if !matches!(event, Event::Tick) {
            tracing::debug!("Event received: {:?}", event);
        }

        // UPDATE: Handle event and update state (Update in Elm)
        handle_event(&mut app, event)?;
    }

    tracing::info!("Application exiting");

    // Cleanup: Restore terminal to normal mode
    tui::restore()?;
    tracing::info!("Terminal restored");

    Ok(())
}
