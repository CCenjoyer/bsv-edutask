import pytest

from pymongo import MongoClient
from pymongo.errors import WriteError
from src.util.dao import DAO
from dotenv import dotenv_values
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="module")
def db_connection():
    """Fixture to create a MongoDB connection."""
    client = MongoClient(dotenv_values('.env').get('MONGO_URL'))
    yield client["test_db"]
    client.drop_database("test_db")
    client.close()

@pytest.fixture
def sut(db_connection):
    with patch('src.util.dao.pymongo.MongoClient') as mock_client:
        mock_sut_client = MagicMock()
        mock_sut_client.edutask = db_connection
        mock_client.return_value = mock_sut_client
        yield DAO("video")
        db_connection.drop_collection("video")

def test_create_valid(sut):
    video_data_valid = {"url": "https://www.google.com/"}
    result = sut.create(video_data_valid)
    assert "_id" in result
    assert "url" in result

def test_create_extra(sut):
    """Test that extra data can still create document."""
    extra_data = {"url": "https://www.google.com/", "extra": "123"}
    result = sut.create(extra_data)
    assert "_id" in result
    assert "extra" in result

@pytest.mark.parametrize("invalid_data", [
    {},
    {"url": 123},
    {"url": None},
    {"string": "https://www.google.com/"},
])
def test_create_invalid(sut, invalid_data):
    """Test that various invalid database data raises a WriteError."""
    with pytest.raises(WriteError):
        sut.create(invalid_data)
