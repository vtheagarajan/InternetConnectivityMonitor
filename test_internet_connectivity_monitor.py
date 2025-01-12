import pytest
from datetime import datetime, timedelta
import csv
import os
#from InternetConnectivityMonitor import OUTAGE_LOG_FILE, get_last_30_days_outages
import InternetConnectivityMonitor
from contextlib import contextmanager

@contextmanager
def temporary_outage_file(temp_path):
    """Context manager to temporarily change the OUTAGE_LOG_FILE path."""
    original_path = InternetConnectivityMonitor.OUTAGE_LOG_FILE  # Assuming it's a module-level variable
    InternetConnectivityMonitor.OUTAGE_LOG_FILE = str(temp_path)
    try:
        yield
    finally:
        InternetConnectivityMonitor.OUTAGE_LOG_FILE = original_path


def test_get_last_30_days_outages(tmp_path):
    # Setup - Create a temporary outage log file with test data
    test_outage_file = tmp_path / "test_outage_log.csv"
    
    # Create test data - mix of records within and outside 30 day window
    today = datetime.now()
    old_date = (today - timedelta(days=40)).strftime('%Y-%m-%d')
    recent_date = (today - timedelta(days=15)).strftime('%Y-%m-%d')
    very_recent_date = (today - timedelta(days=5)).strftime('%Y-%m-%d')
    
    test_data = [
        ["Date", "Start Time", "End Time", "Duration (seconds)"],  # Header
        [old_date, "10:00:00", "10:05:00", "300"],        # Should be excluded
        [recent_date, "14:00:00", "14:10:00", "600"],     # Should be included
        [very_recent_date, "15:00:00", "15:15:00", "900"] # Should be included
    ]
    
    # Write test data to temporary file
    with open(test_outage_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    try:
        with temporary_outage_file(test_outage_file):
            result = InternetConnectivityMonitor.get_last_30_days_outages()
            print(result)
            # Assert
            assert len(result) == 4, "Should return exactly 2 records within 30 days"
            assert result[0][0] == recent_date, "First record should be from 15 days ago"
            assert result[1][0] == very_recent_date, "Second record should be from 5 days ago"
            
            # Verify record structure
            for record in result:
                assert len(record) == 2, "Each record should have 4 fields"
                assert datetime.strptime(record[0], '%Y-%m-%d'), "Date should be in correct format"
                assert ":" in record[1], "Start time should contain colons"
                assert ":" in record[2], "End time should contain colons"
                assert float(record[3]), "Duration should be convertible to float"
            
    except Exception as e:
        pytest.fail(f"Exception raised: {e}")

def test_get_last_30_days_outages_empty_file(tmp_path):
    # Test with empty file
    test_outage_file = tmp_path / "empty_outage_log.csv"
    
    with open(test_outage_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Start Time", "End Time", "Duration (seconds)"])
    
    # Store original path and set new path for test
    original_path = InternetConnectivityMonitor.OUTAGE_LOG_FILE
    InternetConnectivityMonitor.OUTAGE_LOG_FILE = str(test_outage_file)
    
    try:
        result = InternetConnectivityMonitor.get_last_30_days_outages()
        assert len(result) == 0, "Should return empty list for file with only header"
    finally:
        InternetConnectivityMonitor.OUTAGE_LOG_FILE = original_path

def test_get_last_30_days_outages_invalid_data(tmp_path):
    # Test with invalid data
    test_outage_file = tmp_path / "invalid_outage_log.csv"
    
    test_data = [
        ["Date", "Start Time", "End Time", "Duration (seconds)"],
        ["invalid_date", "10:00:00", "10:05:00", "300"],
        ["2023-13-45", "14:00:00", "14:10:00", "600"],  # Invalid date
        ["", "15:00:00", "15:15:00", "900"]  # Empty date
    ]
    
    with open(test_outage_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    # Store original path and set new path for test
    original_path = InternetConnectivityMonitor.OUTAGE_LOG_FILE
    InternetConnectivityMonitor.OUTAGE_LOG_FILE = str(test_outage_file)
    
    try:
        result = InternetConnectivityMonitor.get_last_30_days_outages()
        assert len(result) == 0, "Should handle invalid dates gracefully"
    finally:
        InternetConnectivityMonitor.OUTAGE_LOG_FILE = original_path
