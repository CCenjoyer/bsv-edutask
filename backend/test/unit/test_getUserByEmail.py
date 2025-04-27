import pytest
import unittest.mock as mock

from src.controllers.usercontroller import UserController

@pytest.fixture
def mock_dao():
    return mock.MagicMock()

@pytest.fixture
def user_controller(mock_dao):
    return UserController(dao=mock_dao)

def test_existing_email(user_controller, mock_dao):
    """Test that an existing user is returned correctly."""
    user = {'name': 'test', 'email': 'test@test.com'}
    mock_dao.find.return_value = [user]
    result = user_controller.get_user_by_email('test@test.com')

    assert result == user

def test_non_existing_user(user_controller, mock_dao):
    """Test that a non-existing user returns None if the .find method returns an empty list."""
    mock_dao.find.return_value = []
    result = user_controller.get_user_by_email('test@test.com')

    assert result is None

def test_same_emails(user_controller, mock_dao, capsys):
    """
    Test that if multiple users are found with the same email,
    the first one in the list is returned and a warning is printed.
    """
    user1 = {'nr': '1', 'email': 'test@test.com'}
    user2 = {'nr': '2', 'email': 'test@test.com'}
    mock_dao.find.return_value = [user1, user2]
    result = user_controller.get_user_by_email('test@test.com')
    captured = capsys.readouterr()

    assert "Error: more than one user found with mail test@test.com" in captured.out
    assert result['nr'] == user1['nr']

@pytest.mark.parametrize("invalid_email", [
    "@test.com",
    "test@test",
    "test.com",
    "test@",
    "@.com",
    "@",
    "",
])
def test_invalid_email_format(user_controller, invalid_email):
    """Test that an invalid email format raises a ValueError."""
    with pytest.raises(ValueError) as exc_info:
        user_controller.get_user_by_email(invalid_email)
    assert str(exc_info.value) == 'Error: invalid email address'

def test_dao_exception(user_controller, mock_dao):
    """Test that an exception during dao.find in turn raises an exception."""
    mock_dao.find.side_effect = Exception("DB error")
    with pytest.raises(Exception) as exc_info:
        user_controller.get_user_by_email('test@test.com')
    assert str(exc_info.value) == "DB error"
