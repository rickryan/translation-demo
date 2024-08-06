import azure.cognitiveservices.speech as speechsdk
import re
import logging
logger = logging.getLogger(__name__)

class SpeechProcessor:
    def __init__(self, speech_key, region, audio_stream, target_language="en"):
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
        self.translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=speech_key, region=region)
        self.translation_config.speech_recognition_language = target_language
        self.translation_config.add_target_language(target_language)
        # Create an audio configuration from the provided audio stream
        self.audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        # Use the audio configuration for the TranslationRecognizer
        self.translator = speechsdk.translation.TranslationRecognizer(translation_config=self.translation_config, audio_config=self.audio_config)
        self.speech_buffer = ""

    def start_continuous_recognition(self):
        # Setup event handlers
        self.translator.recognizing.connect(self.on_recognizing)
        self.translator.recognized.connect(self.on_recognized)
        self.translator.session_started.connect(lambda evt: logger.info("Session started: {}".format(evt)))
        self.translator.session_stopped.connect(lambda evt: logger.info("Session stopped: {}".format(evt)))
        self.translator.canceled.connect(self.on_canceled)

        # Start continuous recognition
        logger.debug("Starting recognition.")
        #self.translator.start_continuous_recognition_async()
        self.translator.start_continuous_recognition()

    def stop_continuous_recognition(self):
        self.translator.stop_continuous_recognition_async()

    def on_recognizing(self, evt):
        # Handle intermediate results
        logger.debug(f"Recognizing: {evt.result.text}")
        if evt.result.translations:
            translations = evt.result.translations
            for lang, text in translations.items():
                logger.debug(f"Translated to [{lang}]: {text}")

    def on_recognized(self, evt):
        # Handle final result
        logger.debug(f"On_Recognized: {evt.result.text}")
        if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
            translations = evt.result.translations
            for lang, text in translations.items():
                logger.debug(f"Translated to [{lang}]: {text}")

    def on_canceled(self, evt):
        # Handle cancellation
        logger.debug(f"Recognition canceled: {evt.reason}")
        if evt.reason == speechsdk.CancellationReason.Error:
            logger.error(f"Error details: {evt.error_details}")