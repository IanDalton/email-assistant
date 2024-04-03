import pandas as pd
from streamlit_pages import login
from dotenv import load_dotenv
import os

load_dotenv()
#login.main(os.getenv("GEMINI_API"),os.getenv("USER_EMAIL"),os.getenv("APP_PASSWORD"))
login.main()

