import os
import sys
import openai
import imaplib
import email
from time import sleep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv
load_dotenv()

gmail_host = "imap.gmail.com"
mail = imaplib.IMAP4_SSL(gmail_host)
mail.login(os.getenv("USER_EMAIL"),os.getenv("APP_PASSWORD"))
mail.select("INBOX")


res = mail.search(None, "UNSEEN")
# print all unread emails with the info
for i in res[1][0].split():
    result, data = mail.fetch(i, "(BODY.PEEK[])")
    raw_email = data[0][1]
    raw_email_string = raw_email.decode("utf-8")
    important = False
    
    res, data = mail.fetch(i,"(X-GM-LABELS)")
    info = data[0].decode("utf-8")
    
    tag = info[info.find("\"")+1:
        info.find("\"",
                info.find("\"")+1)]
    if "X-GM-LABELS" in tag:
        tag = "None"
    if "Important" in tag:
        tag = "None"
        important = True
    
    
    email_message = email.message_from_string(raw_email_string)
    print("Tags: "+tag)
    print("Important: "+str(important))
    print("From: " + email_message["From"])
    print("Subject: " + email_message["Subject"])
    print("Date: " + email_message["Date"])
    if email_message.is_multipart():
        for part in email_message.get_payload():
            
            if part.get_content_type() == "text/plain" and len(part.get_payload(decode=True).decode()) > 0:
                print("Body: " + part.get_payload(decode=True).decode())
            elif part.get_content_type() == "text/html":
                soup = BeautifulSoup(part.get_payload(decode=True).decode(), "html.parser")
                print("Body: " + soup.get_text())
    else:
        payload = email_message.get_payload(decode=True)
        if payload is not None:
            print("Body: " + payload.decode())
        else:
            print("Body: None")
    #mail.store(i, '+X-GM-LABELS', 'ApiProcessed')
    print("-------------------------------------------------")

