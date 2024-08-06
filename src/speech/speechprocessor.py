import azure.cognitiveservices.speech as speechsdk
import re
import logging
logger = logging.getLogger(__name__)

# reglar expression that specifies the stop characters for a sentence
STOP_PATTERN = r'[.?!]'
class SpeechProcessor:
    def __init__(self, speech_key, region, target_language="en"):
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
        self.translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=speech_key, region=region)
        self.translation_config.speech_recognition_language = "en-US"
        self.translation_config.add_target_language(target_language)
        # Create an audio configuration from the provided audio stream
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.translator = speechsdk.translation.TranslationRecognizer(translation_config=self.translation_config)
        self.speech_buffer = ""

    def start_continuous_recognition(self):
        # Setup event handlers
        self.translator.recognizing.connect(self.on_recognizing)
        self.translator.recognized.connect(self.on_recognized)
        self.translator.session_started.connect(lambda evt: print("Session started: {}".format(evt)))
        self.translator.session_stopped.connect(lambda evt: print("Session stopped: {}".format(evt)))
        self.translator.canceled.connect(self.on_canceled)

        # Start continuous recognition
        logger.info("Speak into your microphone.")
        self.translator.start_continuous_recognition()

    def stop_continuous_recognition(self):
        self.translator.stop_continuous_recognition()

    def on_recognizing_orig(self, evt):
        # Handle intermediate results
        logger.debug(f"Recognizing: {evt.result.text}")
        if evt.result.translations:
            translations = evt.result.translations
            for lang, text in translations.items():
                print(f"Translated to [{lang}]: {text}")

    def on_recognizing(self, evt):
        # Accumulate speech text
        self.speech_buffer += evt.result.text
        logger.debug(f"Recognizing: {evt.result.text}")
        logger.debug(f"buffer: {self.speech_buffer}")
        match = re.search(STOP_PATTERN, self.speech_buffer)
        if match:
            # The end index of the sentence including the stop character
            end_index = match.end()
            # Extract the sentence up to and including the stop character
            sentence = self.speech_buffer[:end_index]
            # Process the extracted sentence
            self.process_sentence(sentence)
            # Remove the processed section from the speech buffer
            self.speech_buffer = self.speech_buffer[end_index:]
            

    def process_sentence(self, sentence):
        # Placeholder for processing logic, similar to what would be in on_recognized
        logger.debug(f"Processing sentence: {sentence}")
        # Here, you would include any logic that you would have in on_recognized
        
    def on_recognized(self, evt):
        # Handle final result
        print(f"On_Recognized: {evt.result.text}")
        #if evt.result.reason == speechsdk.ResultReason.TranslatedSpeech:
        #    translations = evt.result.translations
        #    for lang, text in translations.items():
        #        print(f"Translated to [{lang}]: {text}")

    def on_canceled(self, evt):
        # Handle cancellation
        logger.debug(f"Recognition canceled: {evt.reason}")
        if evt.reason == speechsdk.CancellationReason.Error:
            logger.error(f"Error details: {evt.error_details}")