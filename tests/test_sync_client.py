"""Test the synchronous client implementation."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time


def test_sync_client_initialization():
    """Test that TessaClient can be initialized."""
    from tessa import TessaClient
    
    client = TessaClient(api_key="test_key")
    assert client._api_key == "test_key"
    assert client._timeout == 60.0
    assert client._max_retries == 3
    client.close()


def test_sync_client_context_manager():
    """Test that TessaClient works as a context manager."""
    from tessa import TessaClient
    
    with TessaClient(api_key="test_key") as client:
        assert client is not None
        assert client._api_key == "test_key"
    # Client should be closed after exiting context


def test_job_class():
    """Test the Job class functionality."""
    from tessa.sync_client import Job
    from tessa import JobStatusEnum, JobStatus
    
    # Create a mock client
    mock_client = Mock()
    
    # Create a job
    job = Job(
        client=mock_client,
        job_id="test_job_123",
        initial_response={
            "job_id": "test_job_123",
            "status": "running",
            "live_url": "https://live.example.com",
            "cdp_url": "ws://cdp.example.com",
            "history_url": "https://history.example.com",
            "polling_url": "https://polling.example.com"
        }
    )
    
    assert job.job_id == "test_job_123"
    assert job.initial_status == "running"
    assert job.live_url == "https://live.example.com"
    assert job.url == "https://history.example.com"
    
    # Test get_status
    mock_status = Mock(spec=JobStatus)
    mock_status.status = JobStatusEnum.COMPLETED
    mock_client.get_job_status.return_value = mock_status
    
    status = job.get_status()
    assert status == mock_status
    mock_client.get_job_status.assert_called_once_with("test_job_123")


def test_job_wait_for_completion():
    """Test job wait_for_completion method."""
    from tessa.sync_client import Job
    from tessa import JobStatusEnum, JobStatus, JobResult
    
    mock_client = Mock()
    
    job = Job(
        client=mock_client,
        job_id="test_job_123",
        initial_response={"job_id": "test_job_123", "status": "running"}
    )
    
    # Mock status responses
    running_status = Mock(spec=JobStatus)
    running_status.status = JobStatusEnum.RUNNING
    
    completed_status = Mock(spec=JobStatus)
    completed_status.status = JobStatusEnum.COMPLETED
    completed_status.output = {"data": "test"}
    completed_status.error = None
    completed_status.credits_used = 10
    completed_status.created_at = None
    completed_status.updated_at = None
    
    # First call returns running, second returns completed
    mock_client.get_job_status.side_effect = [running_status, completed_status]
    
    # Speed up the test by mocking time.sleep
    with patch('time.sleep'):
        result = job.wait_for_completion(poll_interval=1.0)
    
    assert isinstance(result, JobResult)
    assert result.job_id == "test_job_123"
    assert result.status == JobStatusEnum.COMPLETED
    assert result.output == {"data": "test"}
    assert result.credits_used == 10
    assert mock_client.get_job_status.call_count == 2


def test_job_wait_for_completion_timeout():
    """Test job timeout handling."""
    from tessa.sync_client import Job
    from tessa import JobStatusEnum, JobStatus
    from tessa.exceptions import TimeoutError
    
    mock_client = Mock()
    
    job = Job(
        client=mock_client,
        job_id="test_job_123",
        initial_response={"job_id": "test_job_123", "status": "running"}
    )
    
    # Mock status that stays running
    running_status = Mock(spec=JobStatus)
    running_status.status = JobStatusEnum.RUNNING
    mock_client.get_job_status.return_value = running_status
    
    # Test timeout
    with patch('time.sleep'):
        with patch('time.time', side_effect=[0, 0.5, 1.5, 2.5]):  # Simulate time passing
            with pytest.raises(TimeoutError) as exc_info:
                job.wait_for_completion(poll_interval=0.5, timeout=2.0)
    
    assert exc_info.value.job_id == "test_job_123"
    assert exc_info.value.timeout_seconds == 2.0


def test_job_wait_for_completion_failed():
    """Test handling of failed jobs."""
    from tessa.sync_client import Job
    from tessa import JobStatusEnum, JobStatus
    from tessa.exceptions import JobFailedError
    
    mock_client = Mock()
    
    job = Job(
        client=mock_client,
        job_id="test_job_123",
        initial_response={"job_id": "test_job_123", "status": "running"}
    )
    
    # Mock failed status
    failed_status = Mock(spec=JobStatus)
    failed_status.status = JobStatusEnum.FAILED
    failed_status.error = "Something went wrong"
    mock_client.get_job_status.return_value = failed_status
    
    with patch('time.sleep'):
        with pytest.raises(JobFailedError) as exc_info:
            job.wait_for_completion()
    
    assert exc_info.value.job_id == "test_job_123"
    assert exc_info.value.error_message == "Something went wrong"


def test_browser_config():
    """Test BrowserConfig model."""
    from tessa import BrowserConfig
    
    # Default config
    config = BrowserConfig()
    assert config.width == 1920
    assert config.height == 1080
    assert config.residential_ip == False
    assert config.max_duration_minutes == 30
    assert config.idle_timeout_minutes == 2
    
    # Custom config
    custom = BrowserConfig(
        width=1366,
        height=768,
        residential_ip=True,
        max_duration_minutes=60
    )
    assert custom.width == 1366
    assert custom.height == 768
    assert custom.residential_ip == True
    assert custom.max_duration_minutes == 60
    
    # Test validation
    with pytest.raises(Exception):  # Pydantic validation error
        BrowserConfig(width=100)  # Too small
    
    with pytest.raises(Exception):  # Pydantic validation error
        BrowserConfig(height=5000)  # Too large
