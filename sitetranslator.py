import os
import time
import azure.cognitiveservices.speech as speechsdk
import requests, uuid, json
import sys
from azure.messaging.webpubsubservice import WebPubSubServiceClient
import threading
from dotenv import load_dotenv

import webpubsubclient

class SiteTranslator:
    def __init__(self, site_id='site1'):
        self.site_id = site_id
        load_dotenv()
        self.AZURE_REGION = os.getenv('AZURE_REGION')

    def conversation_transcriber_recognition_canceled_cb(self, evt: speechsdk.SessionEventArgs):
        print('Canceled event')

    def conversation_transcriber_session_stopped_cb(self, evt: speechsdk.SessionEventArgs):
        print('SessionStopped event')

    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        print('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if len(evt.result.text.strip()) > 0:
                self.handle_translation(evt.result.text)
            else:
                print('empty text')
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

    def handle_translation(self, text):
        # Implementation for handle_translation
        pass

# Example usage
translator = SiteTranslator(site_id='site2')