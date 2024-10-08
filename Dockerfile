# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Define a build argument to control copying of a .env file
# with environment variables into the container
# when running locally or in a development environment build with the --build-arg flag
# Example: docker build --build-arg COPY_ENV_FILE=true -t my-flask-app .
# otherwise, the .env file will not be copied into the container
# Example: docker build -t my-flask-app .
ARG COPY_ENV_FILE=false
# copy the .env file if it exists and move it to the proper location if COPY_ENV_FILE is true
COPY .en[v] /tmp/.env
RUN if [ "$COPY_ENV_FILE" = "true" ]; then \
        cp /tmp/.env /app/.env; \
    fi
# remove the .env file from the temporary location
RUN if [-f /tmp/.env ]; then rm /tmp/.env; fi

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
#COPY . .
COPY src src
COPY static static
COPY templates templates
COPY languages.json .
COPY server.py .


# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=server.py
ENV FLASK_ENV=production

RUN pip install gunicorn eventlet 
# Run the Flask app
#CMD ["flask", "run", "--host=0.0.0.0"]
# Run the Flask app using Gunicorn with eventlet to handle socket connections properly
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "--worker-class", "eventlet", "server:app"]
