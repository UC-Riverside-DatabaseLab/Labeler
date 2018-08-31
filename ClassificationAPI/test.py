import requests
import json

train_payload = {
    "vectorizer": "tfidf",
    "classifier": "cnn",
    "data": ['sdasda', 'sdagfasgf saf', 'qweagagsdga', 'qweagagsdgasdada'],
    "labels": ['a', 'b', 'a', 'b'],
    "path": "/home/nan/labelingsystem/ClassificationAPI/models"
}
classify_payload = {
    "path": "/home/nan/labelingsystem/ClassificationAPI/models",
    "data": ['sdasda', 'sdagfasgf saf', 'qweagagsdga'],
    "labels": ['a', 'b', 'a'],
}
train_url = "http://localhost:6666/train"
classify_url = "http://localhost:6666/classify"
headers = {'content-type': 'application/json'}
response = requests.post(train_url, data=json.dumps(train_payload), headers=headers)
print(response.text)
response = requests.post(classify_url, data=json.dumps(classify_payload), headers=headers)
print(response.text)
