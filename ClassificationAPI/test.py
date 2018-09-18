import requests
import json


train_payload_a = {'classifier': 'rf', "path": "/home/nan/labelingsystem/ClassificationAPI/models", 'data': ['Want to learn a little more about the origins of our company and how we stay successful? Check out this video: https://www.youtube.com/watch?v=VuukRMmh9-8', 'Had to bring out the shovel this morning and saw this online. Smart phone manufacturers get on it! Our backs will thank you. Drive safe everyone!', 'Hope you had a wonderful and safe holiday!', 'Vary your tweets by either using text,  link or image and with or without hashtag.', 'My twitter has become so powerful that I can actually make my enemies tell the truth.'], 'vectorizer': 'tfidf', 'labels': ['label2', 'label1', 'label2', 'label3', 'label1']}
classify_payload_a = {"path": "/home/nan/labelingsystem/ClassificationAPI/models", 'data': ['Comprehensive up-to-date news coverage, aggregated from sources all over the world by Google News.', 'You could measure the decline of Fox News by the drop in the quality of guests waiting in the green room. ', 'View the latest news and breaking news today for U.S., world, weather, entertainment, politics and health at CNN.com.']}
train_payload = {
    "vectorizer": "tfidf",
    "classifier": "cnn",
    "data": ['s das da', 'sdag fasgf saf', 'qwea ga gsdga', 'afsa as sa ss', 'qweag ag sdgasd ada', 'sdag fassasgf saf'],
    "labels": ['a', 'b', 'a', 'a', 'c', 'a'],
    "path": "/home/nan/labelingsystem/ClassificationAPI/models",
    "word_embedding": "glove"
}
classify_payload = {
    "path": "/home/nan/labelingsystem/ClassificationAPI/models",
    "data": ['sd asd a', 's dagfas gf saf', 'qwe ag ags dga'],
}
train_url = "http://localhost:6666/train"
classify_url = "http://localhost:6666/classify"
headers = {'content-type': 'application/json'}
response = requests.post(train_url, data=json.dumps(train_payload), headers=headers)
print(response.text)
