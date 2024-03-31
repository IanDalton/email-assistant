from mail.inbox import Inbox
from dotenv import load_dotenv
import os

load_dotenv()
inbox = Inbox(os.getenv("USER_EMAIL"),os.getenv("APP_PASSWORD"),"imap.gmail.com","INBOX")
inbox.fetch_mail()
print(inbox.mails)

