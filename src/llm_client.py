import anthropic 
import os 
from dotenv import load_dotenv

load_dotenv()

client=anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

if client:
    print("the api key is found")