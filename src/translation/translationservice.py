# Translation and Publishing Services
import requests
import uuid
import logging
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self, key, region, languages=['en', 'es', 'ar']):
        self.key = key
        self.region = region
        self.endpoint = "https://api.cognitive.microsofttranslator.com"
        self.to_languages = languages

    def translate(self, text):
        path = '/translate'
        constructed_url = self.endpoint + path
        params = {
            'api-version': '3.0',
            'from': 'en',
            'to': self.to_languages
        }
        headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = [{'text': text}]
        response = requests.post(constructed_url, params=params, headers=headers, json=body).json()
        return response[0]['translations']
