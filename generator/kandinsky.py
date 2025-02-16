import base64
import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

apikey = os.getenv('API_KEY')
secretkey = os.getenv('SECRET_KEY')
path_save = os.getenv('PATH_SAVE')

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models',
                                headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run',
                                 headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=20):
        while attempts > 0:
            response = requests.get(
                self.URL + 'key/api/v1/text2image/status/' + request_id,
                headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

if __name__ == '__main__':
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', apikey, secretkey)
    model_id = api.get_model()
    n = 0

    if not os.path.exists(path_save):
        os.makedirs(path_save)
        print(f"Создана директория: {path_save}")

    promt_ = open("out.txt", "r", encoding="utf8")
    for i in promt_.readlines():
        print(i)
        uuid = api.generate(i, model_id)
        images = api.check_generation(uuid)
        images = str(images)
        image_data = base64.b64decode(images)
        with open(os.path.join(path_save, f"{n}.png"), 'wb') as file:
            file.write(image_data)
        print(f"Файл {i}.png;")
        n += 1
