import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError
import time

# Correct import path for the decorator
from hutch_bunny.core.db_manager import WakeAzureDB

# Mock settings to simulate the environment
mock_settings = MagicMock()
mock_settings.DATASOURCE_DB_DRIVERNAME = "mssql"

# Sample function to decorate
@WakeAzureDB(retries=2, delay=1, error_code="40613")
def sample_function():
    pass

def test_no_error():
    with patch('hutch_bunny.core.db_manager.settings', mock_settings):
        # Test normal execution
        sample_function()

def test_with_error():
    with patch('hutch_bunny.core.db_manager.settings', mock_settings):
        # Mock sleep to avoid actual delay
        with patch('time.sleep', return_value=None):
            # Simulate function failure with relevant error code
            error = OperationalError("Dummy", "Dummy", "40613")
            with patch('hutch_bunny.core.db_manager.sample_function', side_effect=error) as mock_func:
                with pytest.raises(OperationalError):
                    sample_function()
                assert mock_func.call_count == 3  # Initial call + 2 retries

def test_with_different_error():
    with patch('hutch_bunny.core.db_manager.settings', mock_settings):
        # Test with a different error code, should not retry
        error = OperationalError("Dummy", "Dummy", "DifferentError")
        with patch('hutch_bunny.core.db_manager.sample_function', side_effect=error) as mock_func:
            with pytest.raises(OperationalError):
                sample_function()
            assert mock_func.call_count == 1  # No retries

if __name__ == "__main__":
    pytest.main()
