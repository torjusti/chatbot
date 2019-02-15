from pymongo import TEXT
import os
import json

from model.ModelFactory import ModelFactory

fact = ModelFactory.get_instance()


def test_get_document():
    global fact
    with open("model/test/test_data/test_data_model_factory.json", 'r') as f:
        data = json.load(f)
    fact.set_database("agent25.tinusf.com", "test_db",
                      str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

    fact.post_document(data[0], "test")
    fact.post_document(data[1], "test")
    fact.get_collection("test").create_index(
        [("keywords", TEXT), ("content.keywords.keyword", TEXT)], default_language="norwegian")

    # Test first document
    assert fact.get_document("emne test", "test")['content'] == data[0]['content']
    assert fact.get_document("emne skole arbeid", "test")['content'] == data[0]['content']

    # Test second document
    assert fact.get_document("bra test", "test")['content'] == data[1]['content']
    assert fact.get_document("bra arbeid emne", "test")['content'] == data[1]['content']

    # Test gibberish should not give a document
    assert not fact.get_document("sakfscfdsojimad", "test")

    fact.get_database().drop_collection("test")


def test_update_document():
    global fact
    data = '{"name": "testname"}'
    fact.set_database("agent25.tinusf.com", "test_db",
                      str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

    fact.post_document(data, "test")
    fact.get_collection("test").create_index(
        [("name", TEXT)], default_language="norwegian")

    newdata = '{"name": "nottestname"}'
    fact.update_document({"name": "testname"}, newdata, "test")
    doc = fact.get_document("nottestname", "test")

    fact.get_database().drop_collection("test")

    assert doc["name"] == "nottestname"
