import json
import time
import azure.cognitiveservices.speech as speechsdk
from .speechprocessor import SpeechProcessor

class Transcriber:
    def __init__(self, speech_processor: SpeechProcessor, translator, publisher):
        self.speech_processor = speech_processor
        speech_config = speech_processor.speech_config
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        audio_config = self.speech_recognizer.recognize_once_async().get()
        self.conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)
        self.publisher = publisher
        self.translator = translator
        self.transcribing_stop = False

    def connect_callbacks(self):
        self.conversation_transcriber.transcribed.connect(self.conversation_transcriber_transcribed_cb)
        self.conversation_transcriber.session_started.connect(self.conversation_transcriber_session_started_cb)
        self.conversation_transcriber.session_stopped.connect(self.conversation_transcriber_session_stopped_cb)
        self.conversation_transcriber.canceled.connect(self.conversation_transcriber_recognition_canceled_cb)
        # stop transcribing on either session stopped or canceled events
        self.conversation_transcriber.session_stopped.connect(self.stop_cb)
        self.conversation_transcriber.canceled.connect(self.stop_cb)

    def start_transcribing_async(self):
        self.connect_callbacks()
        self.conversation_transcriber.start_transcribing_async()
        self.wait_for_completion()

    def stop_transcribing_async(self):
        self.conversation_transcriber.stop_transcribing_async()

    def wait_for_completion(self):
        while not self.transcribing_stop:
            time.sleep(.5)

    def handle_translation(self, text):
        try:
            recognized_text = self.speech_processor.recognize_speech()
            if recognized_text:
                translations = self.translator.translate(recognized_text)
                for translation in translations:
                    data = {
                        "language": translation['to'],
                        "translation": translation['text']
                    }
                    self.publisher.send_to_all(json.dumps(data))
                    print(f"Published translation to {translation['to']}: {translation['text']}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Callback methods
    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        print('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if len(evt.result.text.strip()) > 0:
                self.handle_translation(evt.result.text)
            else:
                print('empty text')
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

    def conversation_transcriber_session_started_cb(self, args):
        print('SessionStarted event')
        print("Speak into your microphone.")

    def conversation_transcriber_session_stopped_cb(self, args):
        print('SessionStopped event')

    def conversation_transcriber_recognition_canceled_cb(self, args):
        print('Canceled event')

    def stop_cb(self, args):
        self.transcribing_stop = True

# Usage example
# Assuming recognize_from_file() is supposed to be replaced or refactored to use this class
def recognize_from_file():
    transcriber = Transcriber()
    transcriber.start_transcribing_async()
    transcriber.stop_transcribing_async()

if __name__ == '__main__':
    try:
        recognize_from_file()
    except Exception as e:
        print(f"An error occurred: {e}")