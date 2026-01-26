"""Unit tests for scheduler service."""

import pytest
from unittest.mock import MagicMock, patch

from app.services.scheduler import (
    get_scheduler_status,
    scheduler,
    start_scheduler,
    stop_scheduler,
    surfacing_job,
    cleanup_job,
)


@pytest.mark.asyncio
async def test_surfacing_job_executes():
    """Test surfacing job placeholder executes without errors."""
    # Should not raise any exceptions
    await surfacing_job()


@pytest.mark.asyncio
async def test_cleanup_job_executes():
    """Test cleanup job placeholder executes without errors."""
    # Should not raise any exceptions
    await cleanup_job()


def test_start_scheduler_when_enabled(reset_singleton):
    """Test scheduler starts successfully when enabled in config."""
    # Mock configuration
    mock_config = MagicMock()
    mock_config.scheduler = {
        "enabled": True,
        "surfacing_interval_seconds": 300,  # 5 minutes for testing
        "batch_size": 50,
    }

    with patch("app.services.scheduler.get_config", return_value=mock_config):
        with patch.object(scheduler, "add_job") as mock_add_job:
            with patch.object(scheduler, "start") as mock_start:
                # Start the scheduler
                start_scheduler()

                # Verify surfacing job was added with correct interval
                calls = mock_add_job.call_args_list
                assert len(calls) == 2  # surfacing_job and cleanup_job

                # Check surfacing job
                surfacing_call = calls[0]
                assert surfacing_call.kwargs["seconds"] == 300
                assert surfacing_call.kwargs["id"] == "surfacing_job"

                # Check cleanup job
                cleanup_call = calls[1]
                assert cleanup_call.kwargs["hour"] == 2
                assert cleanup_call.kwargs["minute"] == 0
                assert cleanup_call.kwargs["id"] == "cleanup_job"

                # Verify scheduler was started
                mock_start.assert_called_once()


def test_start_scheduler_when_disabled(reset_singleton):
    """Test scheduler skips initialization when disabled in config."""
    # Mock configuration with scheduler disabled
    mock_config = MagicMock()
    mock_config.scheduler = {
        "enabled": False,
        "surfacing_interval_seconds": 86400,
        "batch_size": 50,
    }

    with patch("app.services.scheduler.get_config", return_value=mock_config):
        with patch.object(scheduler, "start") as mock_start:
            # Start the scheduler
            start_scheduler()

            # Verify scheduler was NOT started
            mock_start.assert_not_called()


def test_start_scheduler_uses_config_values(reset_singleton):
    """Test scheduler uses values from configuration."""
    # Mock configuration with custom values
    mock_config = MagicMock()
    mock_config.scheduler = {
        "enabled": True,
        "surfacing_interval_seconds": 7200,  # 2 hours
        "batch_size": 100,
    }

    with patch("app.services.scheduler.get_config", return_value=mock_config):
        with patch.object(scheduler, "add_job") as mock_add_job:
            with patch.object(scheduler, "start"):
                # Start the scheduler
                start_scheduler()

                # Verify surfacing job uses custom interval
                surfacing_call = mock_add_job.call_args_list[0]
                assert surfacing_call.kwargs["seconds"] == 7200


def test_start_scheduler_failure_raises_error(reset_singleton):
    """Test scheduler startup failure raises RuntimeError."""
    # Mock configuration
    mock_config = MagicMock()
    mock_config.scheduler = {
        "enabled": True,
        "surfacing_interval_seconds": 86400,
        "batch_size": 50,
    }

    with patch("app.services.scheduler.get_config", return_value=mock_config):
        with patch.object(scheduler, "add_job", side_effect=Exception("Test error")):
            # Verify RuntimeError is raised
            with pytest.raises(RuntimeError, match="Scheduler initialization failed"):
                start_scheduler()


def test_stop_scheduler_when_running():
    """Test scheduler stops gracefully when running."""
    with patch.object(type(scheduler), "running", new_callable=lambda: property(lambda self: True)):
        with patch.object(scheduler, "shutdown") as mock_shutdown:
            # Stop the scheduler
            stop_scheduler()

            # Verify shutdown was called with wait=True
            mock_shutdown.assert_called_once_with(wait=True)


def test_stop_scheduler_when_not_running():
    """Test scheduler stop is safe when not running."""
    with patch.object(type(scheduler), "running", new_callable=lambda: property(lambda self: False)):
        with patch.object(scheduler, "shutdown") as mock_shutdown:
            # Stop the scheduler
            stop_scheduler()

            # Verify shutdown was not called
            mock_shutdown.assert_not_called()


def test_stop_scheduler_error_handling():
    """Test scheduler stop handles errors gracefully."""
    with patch.object(type(scheduler), "running", new_callable=lambda: property(lambda self: True)):
        with patch.object(scheduler, "shutdown", side_effect=Exception("Test error")):
            # Should not raise - errors are logged
            stop_scheduler()


def test_get_scheduler_status_running():
    """Test get_scheduler_status returns 'running' when scheduler is running."""
    with patch.object(type(scheduler), "running", new_callable=lambda: property(lambda self: True)):
        assert get_scheduler_status() == "running"


def test_get_scheduler_status_stopped():
    """Test get_scheduler_status returns 'stopped' when scheduler is stopped."""
    with patch.object(type(scheduler), "running", new_callable=lambda: property(lambda self: False)):
        scheduler.state = 0  # STATE_STOPPED
        assert get_scheduler_status() == "stopped"


def test_get_scheduler_status_not_initialized():
    """Test get_scheduler_status returns 'not_initialized' for other states."""
    with patch.object(type(scheduler), "running", new_callable=lambda: property(lambda self: False)):
        scheduler.state = 1  # Any state != 0
        assert get_scheduler_status() == "not_initialized"
