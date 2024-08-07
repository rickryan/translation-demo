import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import logging
logger = logging.getLogger(__name__)

load_dotenv()
endpoint = os.getenv["AZURE_OPENAI_ENDPOINT"]
deployment = os.getenv["CHAT_COMPLETIONS_DEPLOYMENT_NAME"]
api_key = os.getenv("OPENAI_API_KEY")
api_version = "2024-02-01"
token_provider = DefaultAzureCredential()

#token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    #azure_ad_token_provider=token_provider,
    api_version="2024-02-01",
)

prompt = "Generate a summary and bullets in the specified language for three main points of the below conversation in the following JSON format:/n{ \"summary\" : \"summary of talk\",\"points\" : [\"point1\",\"point2\",\"point3\"]}/n"

def summarize(text: str, language: str) -> dict:
    '''Returns a summary of the input text in the specified language
    Output:
    result: dict, the result of the summarization in the format
    {
        "summary" : "summary of talk",
        "points" : ["point1","point2","point3"],
        "language" : "en"
    }    
    '''
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"/nLanguage: {language} /nConversation:/n {text}"},
        ],
        temperature=0.3,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    
    # create a result object that contains the content of the response
    result = response.choices[0].message.content
    # convert the result string that is json to an object
    result = json.loads(result)
    result['language'] = language
    logger.debug(type(result))
    
    return result

# insert an if main block that tests the summarize function
if __name__ == "__main__":
    text = "Good morning, team! Gather 'round, gather 'round. Let's get ready to tackle another day of package magic! Just like a well-oiled machine, we need all our parts working together smoothly to keep this place running like a Swiss watch. So, let's dive into our pre-shift briefing.\n\nFirst off, a quick note from our friends in HR. Remember to update your contact information in the system if you haven't already. It's as important as checking the oil in your car – it keeps everything running smoothly and ensures we can reach you if needed. So, if you’ve moved, changed your number, or got a new email address, make sure it’s updated. \n\nNow, on to safety – our number one priority. Think of safety like the GPS in your car. It might seem like it's just there in the background, but without it, you’d be lost. Here are today’s safety highlights:\n\nStay Alert. The automated sorting equipment is our best friend and sometimes our biggest challenge. Always stay aware of your surroundings. Remember, those machines don’t have eyes, so we have to be theirs.\n\nProper Lifting Techniques. Bend those knees and keep your back straight. You're not Hercules – even if you feel like it after that third cup of coffee!\n\nEmergency Exits. Know where they are and make sure they're never blocked. It's like knowing the escape route in a video game – always be prepared for the unexpected.\n\nAlright, on to our goals for the shift. Today, we’re aiming to sort and process 10,000 packages. That’s a lot, but I know we can do it. Let’s break it down:\n\nSpeed. Keep up the pace but don’t sacrifice accuracy. Like a NASCAR pit crew, every second counts, but so does every detail.\nQuality. Make sure every package is handled with care. Remember, these packages could be someone’s birthday gift, a long-awaited order, or even a precious heirloom.\nTeamwork. Help each other out. If you see someone struggling, lend a hand. We’re not just a team, we’re a family – and families support each other.\n\nFinally, a little something to look forward to. Mark your calendars for next Friday,  we’re having a team-building event! It’s going to be a warehouse Olympics, complete with a package"
    x = summarize(text, "en")
    print(x)
    x = summarize(text, "fr")
    print(x)
