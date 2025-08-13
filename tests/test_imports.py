"""Test that all main imports work correctly."""

import pytest


def test_main_imports():
    """Test that main classes can be imported."""
    from tessa import BrowserAgent, TessaClient, AsyncTessaClient
    from tessa import BrowserConfig, JobStatus, JobResult, ActionSelectionModel
    from tessa import TessaError, AuthenticationError, RateLimitError
    
    # Verify classes exist
    assert BrowserAgent is not None
    assert TessaClient is not None
    assert AsyncTessaClient is not None
    assert BrowserConfig is not None
    

def test_model_enums():
    """Test that model enums work correctly."""
    from tessa import ActionSelectionModel
    
    assert ActionSelectionModel.CLAUDE_SONNET.value == "claude-sonnet-4-20250514"
    assert ActionSelectionModel.GPT_4O.value == "gpt-4o"
    assert ActionSelectionModel.GEMINI_FLASH.value == "gemini/gemini-2.5-flash"
    
    # Test default
    assert ActionSelectionModel.default() == ActionSelectionModel.CLAUDE_SONNET


def test_browser_config():
    """Test BrowserConfig model."""
    from tessa import BrowserConfig
    
    config = BrowserConfig()
    assert config.width == 1920
    assert config.height == 1080
    assert config.residential_ip == False
    assert config.max_duration_minutes == 30
    assert config.idle_timeout_minutes == 2
    
    # Test with custom values
    custom = BrowserConfig(
        width=1366,
        height=768,
        residential_ip=True
    )
    assert custom.width == 1366
    assert custom.height == 768
    assert custom.residential_ip == True


def test_exceptions():
    """Test custom exceptions."""
    from tessa.exceptions import (
        TessaError,
        AuthenticationError,
        JobFailedError,
        ValidationError
    )
    
    # Test base exception
    err = TessaError("Test error", {"detail": "test"})
    assert str(err) == "Test error"
    assert err.details == {"detail": "test"}
    
    # Test auth error
    auth_err = AuthenticationError()
    assert "Invalid authentication" in str(auth_err)
    
    # Test job failed error
    job_err = JobFailedError("job123", "Network error")
    assert "job123" in str(job_err)
    assert "Network error" in str(job_err)
    assert job_err.job_id == "job123"
    
    # Test validation error
    val_err = ValidationError("Invalid input", ["field1 required", "field2 invalid"])
    assert val_err.errors == ["field1 required", "field2 invalid"]
