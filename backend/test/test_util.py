import pytest
from unittest.mock import patch, MagicMock
from proxmox_api import util



# Test to subscribe hosting_api real adh6 account to the ML.
@patch('proxmox_api.util.adh6_search_user')
@patch('proxmox_api.util.requests.get')
@patch('proxmox_api.util.requests.put')
def test_subscribe_to_hosting_ML(mock_put, mock_get, mock_search_user):
    # Mock the search user function to return a user id
    mock_search_user.return_value = [123]
    
    # Mock the account info request
    mock_account_response = MagicMock()
    mock_account_response.json.return_value = {
        "username": "hosting_api",
        "mailinglist": 4  # binary 100 -> new value will be 110 = 6
    }
    mock_get.return_value = mock_account_response
    
    # Mock the ML status update request
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200  # ADH6 returns 200 on success
    mock_put.return_value = mock_put_response
    
    _, status = util.subscribe_to_hosting_ML("hosting_api")
    assert status == 200

