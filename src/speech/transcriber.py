import json
import time
import azure.cognitiveservices.speech as speechsdk
from .socketspeechprocessor import SpeechProcessor
import logging
logger = logging.getLogger(__name__)
class Transcriber:
    def __init__(self, speech_processor: SpeechProcessor, translator, publisher):
        self.speech_processor = speech_processor
        speech_config = speech_processor.speech_config
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        audio_config = self.speech_processor.audio_config
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
        logger.debug(f'Translating:{text}')
        try:
            if text:
                translations = self.translator.translate(text)
                for translation in translations:
                    data = {
                        "language": translation['to'],
                        "translation": translation['text']
                    }
                    self.publisher.send_to_all(json.dumps(data))
                    logger.debug(f"Published translation to {translation['to']}: {translation['text']}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    # Callback methods
    def conversation_transcriber_transcribed_cb(self, evt: speechsdk.SpeechRecognitionEventArgs):
        logger.debug('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if len(evt.result.text.strip()) > 0:
                self.handle_translation(evt.result.text)
            else:
                logger.debug('empty text')
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            logger.warn('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

    def conversation_transcriber_session_started_cb(self, args):
        logger.info('SessionStarted event')

    def conversation_transcriber_session_stopped_cb(self, args):
        logger.info('SessionStopped event')

    def conversation_transcriber_recognition_canceled_cb(self, args):
        logger.info('Canceled event')

    def stop_cb(self, args):
        self.transcribing_stop = True
        
    def is_transcribing(self):
        return not self.transcribing_stop
