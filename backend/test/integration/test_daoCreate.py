import pytest
import pymongo

from pymongo.errors import WriteError
from src.util.dao import DAO
from dotenv import dotenv_values

@pytest.fixture
def db_connection():
    """Fixture to connect to database and create a test database."""
    client = pymongo.MongoClient(dotenv_values('.env').get('MONGO_URL'))
    db = client['test_db']
    yield db
    client.drop_database('test_db')
    client.close()

@pytest.fixture
def sut(db_connection):
    dao = DAO("video")
    dao.db = db_connection
    dao.collection = dao.db["video"]
    yield dao
    db_connection.drop_collection("video")

def test_create_valid(sut):
    video_data_valid = {"url": "https://www.google.com/"}
    result = sut.create(video_data_valid)
    assert "_id" in result

def test_create_no_data(sut):
    no_data = {}
    with pytest.raises(WriteError):
        sut.create(no_data)

def test_create_extra(sut):
    extra_data = {"url": "https://www.google.com/", "extra": "123"}
    result = sut.create(extra_data)
    assert "_id" in result

def test_wrong_data_type(sut):
    value_wrong_type = {"url": 123}
    with pytest.raises(WriteError):
        sut.create(value_wrong_type)

def test_create_value_none(sut):
    video_data_none_value = {"url": None}
    with pytest.raises(WriteError):
        sut.create(video_data_none_value)