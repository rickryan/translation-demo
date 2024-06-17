import azure.cognitiveservices.speech as speechsdk

# Speech Recognition and Processing
class SpeechProcessor(speechsdk.SpeechRecognizer):
    def __init__(self, speech_key, region):
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
        self.speech_config.endpoint_silence_timeout_ms = 1
        self.speech_config.speech_recognition_language="en-US"
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)

    def recognize_speech(self):
        print("Speak into your microphone.")
        result = self.speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")