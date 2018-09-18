from background_task import background
import json
import requests


@background(schedule=20)
def query_api(url, payload, headers):
  response = requests.post(url, data=json.dumps(payload), headers=headers)
  if response.status_code != 200:
    raise Exception(response.text)
