# Refactored main.py

import os
import time
import requests
import json
import threading
from dotenv import load_dotenv
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from webpubsubclient import WebPubSubClient
from src.translation.translationservice import TranslationService
from src.speech.speechprocessor import SpeechProcessor
from src.speech.transcriber import Transcriber
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()
AZURE_REGION = os.getenv('AZURE_REGION')
TRANSLATOR_KEY = os.getenv('TRANSLATOR_KEY')
PUBSUB_ENDPOINT = os.getenv('PUBSUB_ENDPOINT')
PUBSUB_HUBNAME = os.getenv('PUBSUB_HUBNAME')


# Main Functionality
def main():
    speech_processor = SpeechProcessor(os.getenv('SPEECH_KEY'), AZURE_REGION)
    translation_service = TranslationService(TRANSLATOR_KEY, AZURE_REGION)
    connection_string = os.getenv("PUBSUB_ENDPOINT")
    publish_service = WebPubSubClient(connection_string, 'site1')
    

    transcriber = Transcriber(speech_processor, translation_service, publish_service)
    #transcriber = Transcriber()
    transcriber.start_transcribing_async()
    transcriber.stop_transcribing_async()
    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True
        

        # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)

    
def testit():    
    speech_processor = SpeechProcessor(os.getenv('SPEECH_KEY'), AZURE_REGION)
    translation_service = TranslationService(TRANSLATOR_KEY, AZURE_REGION)
    connection_string = os.getenv("PUBSUB_ENDPOINT")
    publish_service = WebPubSubClient(connection_string, 'site1')
    try:
        recognized_text = speech_processor.recognize_speech()
        if recognized_text:
            translations = translation_service.translate(recognized_text)
            for translation in translations:
                data = {
                    "language": translation['to'],
                    "translation": translation['text']
                }
                publish_service.send_to_all(json.dumps(data))
                print(f"Published translation to {translation['to']}: {translation['text']}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()