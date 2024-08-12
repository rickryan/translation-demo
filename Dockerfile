# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg and ALSA utilities
RUN apt-get update && apt-get install -y ffmpeg alsa-utils alsa-oss

# Set environment variables to use the dummy audio device
ENV AUDIODEV=hw:0,0
ENV ALSA_CARD=0

# Create ALSA configuration file to use a null device
RUN echo "pcm.!default { type plug slave.pcm "null" }" > /etc/asound.conf && \
    echo "ctl.!default { type hw card 0 }" >> /etc/asound.conf

# Copy the Flask app files into the container
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=server.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
