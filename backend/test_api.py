from google.genai import Client
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('API key loaded:', bool(api_key))
if api_key:
    client = Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say hello in JSON format: {"message": "hello"}'
        )
        print('Response type:', type(response))
        print('Response dir:', [x for x in dir(response) if not x.startswith('_')])
        if hasattr(response, 'text'):
            print('Has text attr:', True)
            print('Text content:', repr(response.text))
        else:
            print('No text attr')
        print('Full response:', response)
    except Exception as e:
        print('Error:', e)