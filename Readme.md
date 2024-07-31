# Real-time Translation using Azure Speech, Translation and PubSub Services
This application is a real-time translation and speech-to-text demo. It utilizes Azure services such as Web PubSub, Translator, Speech, and OpenAI to enable translation, transfer and summarization of spoken messages to a browser. The server can be started and accessed via API endpoints.  The output is displayed on the endpoint index.html.  Ausio input via a microphone may be accessed via a web app at speaker.html or running a local app, main.py. Additionally, there is a test mode available for recording and summarizing English text.

## Prerequisites

1. [python](https://www.python.org/)
2. Create an Azure Web PubSub resource
3. Create an Azure Translator resource
4. Create an Azure Speech services resource
5. Create an Azure openAI services resource
6. (optional) Install ffmpeg if you plan to use the the web app and page speaker.html for input

## Setup

```bash
# Create venv
python -m venv env
# Active venv
source .env/bin/activate
# pip install
pip install -r requirements.txt
```

Install ffmpeg on the server machine if you intend to use the web app and page speaker.html for audio input.
*Note: ffmpeg is required to convert the audio from a browser in .webm format to .wav format required by Azure Speech services.*

## Environment Setup

API keys, connection details such as strings and regions are set via environment variables.  They may either be set in system environment variables or via the .env file.  An example .env file is provided in the .env_example file.  To create the .env file copy the .env_example file and edit the values.

Varaibles required:
* AZURE_REGION - Azure region, e.g. 'eastus'
* TRANSLATOR_KEY - Azure translation API key from **Keys and Endpoint** tab of Azure Translator service
* PUBSUB_ENDPOINT - **Connection String** from **Keys** tab of the created Azure Web PubSub service
* PUBSUB_HUBNAME - identifier for the pub/sub topic, e.g., "sample_stream"
* SPEECH_KEY - Azure speech API key from **Keys and Endpoint** tab of Azure Speech service
* AZURE_OPENAI_ENDPOINT - URL to the endpoint **Keys and Endpoint** tab of Azure Open AI service
* CHAT_COMPLETIONS_DEPLOYMENT_NAME - deployment name of the resource from the **Deployments** tab of **Azure Open AI Studio**
* OPENAI_API_KEY - Azure openAI API key from **Keys and Endpoint** tab of Azure Open AI service

## Start the server

```bash
python server.py 
```

The server is then started. Open `http://localhost:5000/<sitename>` in browser. You can use any name as sitename.  If you use F12 to view the Network you can see the WebSocket connection is established.

The server may also be accessed via an API via the endpoints documented in [api-definitions.md](/api-definitions.md)

Audio input may be done through the a local python app, main.py, or via the web page `http://localhost:5000/<sitename>/speaker`

## To start the local app, main.py

Run:

```bash
source ./env/bin/activate
python main.py
```

The main app should use your system's default microphone.  Start speaking messages and you can see the messages are translated and transferred to the browser.

## Test Mode

There is a test mode available which creates a test_site and displays the english text that it recorded via the microphone.  It also prefills the the english text box with an example recording to enable testing of the summarization without having to speak the complete text into the microphone.  To go to the test site open `http://localhost:5000/test` in a browser.