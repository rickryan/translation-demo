import subprocess
import threading
import logging

class AudioStreamConverter:
    def __init__(self, input_queue, output_stream):
        self.input_queue = input_queue
        self.output_stream = output_stream
        self.process = None

    def prepare_ffmpeg(self):
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', 'pipe:0',     # Read from stdin
            '-f', 'wav',        # Output format
            '-ar', '16000',     # Set sample rate to 16kHz
            'pipe:1'            # Write to stdout
        ]
        self.process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _write_to_output_stream(self):
        """Reads data from ffmpeg stdout and writes it to the provided output stream."""
        try:
            for data in iter(lambda: self.process.stdout.read(1024), b''):
                self.output_stream.write(data)
        except Exception as e:
            logging.error(f"Error writing to output stream: {e}")
        finally:
            logging.debug("Closing output stream.")
            self.output_stream.close()

    def convert_stream(self):
        logging.debug("Starting stream conversion.")
        self.prepare_ffmpeg()
        # Start a thread to write ffmpeg's output to the provided output stream
        threading.Thread(target=self._write_to_output_stream).start()
        try:
            while True:
                data = self.input_queue.get()
                if data is None:
                    break
                logging.debug(f"Writing {len(data)} bytes to ffmpeg stdin.")
                self.process.stdin.write(data)
            self.process.stdin.close()
            self.process.wait()
        except Exception as e:
            logging.error(f"Error during streaming: {e}")
        finally:
            logging.debug("Exiting convert stream to cleanup.")
            self.cleanup()

    def cleanup(self):
        if self.process:
            logging.debug(self.process.stderr.read())
            self.process.terminate()
            self.process.wait()
        logging.debug("Cleanup completed.")
