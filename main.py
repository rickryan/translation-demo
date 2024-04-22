import os
import time
import azure.cognitiveservices.speech as speechsdk
import requests, uuid, json
import sys
from azure.messaging.webpubsubservice import WebPubSubServiceClient
import threading


def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
    print('Canceled event')

def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStopped event')

def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    print('TRANSCRIBED:')
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        handle_translation(evt.result.text)
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

def handle_publish(translations):
    connection_string = "Endpoint=https://pb-transalate-demo-ps.webpubsub.azure.com;AccessKey=8A7R1e1gwVAba6VsZP6qEUXVTnFZypFFw8ys6HdwPAI=;Version=1.0;"
    hub_name = "sample_stream"
    message = translations

    service = WebPubSubServiceClient.from_connection_string(connection_string, hub=hub_name)
    res = service.send_to_all(message, content_type='text/plain')
    print(res)

def process_translation(translation):
    target_language = translation['to']
    translated_text = translation['text']
    print(f"Translation to {target_language}: {translated_text}")

    data = {
        "language": target_language,
        "translation": translated_text
    }

    json_text = json.dumps(data)
    handle_publish(json_text)

def handle_translation(text):
    key = "fb2363d155f445f6a8d0b2becf463cbe"
    endpoint = "https://api.cognitive.microsofttranslator.com"

    location = "eastus2"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': ['en','bg', 'es','ar','hi', 'zh-Hans','fr']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': text
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    translations = response[0]['translations']
 
    print(f"Original Speech to: {text}")

    threads = []
    for translation in translations:
        thread = threading.Thread(target=process_translation, args=(translation,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStarted event')

def recognize_from_file():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription="5a8ea0c813f144ac9efd5f877d4a46a4", region="eastus2")
    speech_config.speech_recognition_language="en-US"
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Speak into your microphone.")
    audio_config = speech_recognizer.recognize_once_async().get()

    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
    conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
    conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
    conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)
    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(5)

    conversation_transcriber.stop_transcribing_async()

# Main

try:
    recognize_from_file()
except Exception as err:
    print("Encountered exception. {}".format(err))