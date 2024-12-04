import os
# uncomment the line below if you are using a .env file
#from dotenv import load_dotenv
#load_dotenv()

JAMF_API_URL = os.getenv("JAMF_API_URL")
JAMF_USERNAME = os.getenv("JAMF_USERNAME")
JAMF_PASSWORD = os.getenv("JAMF_PASSWORD")
SNIPEIT_API_URL = os.getenv("SNIPEIT_API_URL")
SNIPEIT_API_TOKEN = os.getenv("SNIPEIT_API_TOKEN")

