import imaplib
import smtplib
import email
import re
import os
import datetime as dt

from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#TODO: On the menu it has to ask what inbox is the sent inbox

class Mail:
    def __init__(self,mail: imaplib.IMAP4_SSL,id,user_email,user_passwrd,type="inbound") -> None:
        # Email controller from the user
        self.mail = mail
        self.user_email = user_email
        self.user_passwrd = user_passwrd
        # TODO: Change this so it checks the inbox db to get the actual name
        self.mail.select("INBOX"if type == "inbound" else "[Gmail]/Enviados")
        
        self.id = id
        
        # Getting the email tags with some regex magic
        self.is_important = False

        info = mail.fetch(id,"(X-GM-LABELS)")[1][0].decode("utf-8")
        tags = re.findall(r'"(.*?)"', info)

        self.is_important = "Important" in tags
        tags = [tag for tag in tags if tag not in ["X-GM-LABELS", "Important"]]

        self.tags = tags  
        
        # Getting the email data without marking it as read.  
        _,data = mail.fetch(id, "(BODY.PEEK[])")
        raw_email_string = data[0][1].decode("utf-8")
        
        email_message = email.message_from_string(raw_email_string)
        self.mail_from = email_message["From"]
        self.subject = email_message["Subject"]
        self.date = email_message["Date"]
        #self.date = dt.datetime.strptime(email_message["Date"],'%a, %d %b %Y %H:%M:%S %z')
        self.in_reply_to = email_message.get("In-Reply-To")
        self.message =email_message
        # Getting the email body
        self.body = ""
        
        # The email might be a chain of emails, so we need to check if it is multipart
        if email_message.is_multipart():
            part = email_message.get_payload(0)

            if part.get_content_type() == "text/plain" and len(part.get_payload(decode=True).decode()) > 0:
                self.body += part.get_payload(decode=True).decode()
            elif part.get_content_type() == "text/html":
                soup = BeautifulSoup(part.get_payload(decode=True).decode(), "html.parser")
                self.body += soup.get_text()
        else:
            payload = email_message.get_payload(decode=True)
            if payload is not None:
                self.body += payload.decode()
            else:
                self.body = None

    def mark_as_read(self):
        self.mail.store(self.id, '+FLAGS', '\\Seen')
        
    def respond(self, response_body, smtp_server='smtp.gmail.com', smtp_port=587):
        msg = MIMEMultipart()
        msg['From'] = self.user_email
        msg['To'] = self.mail_from
        msg['Subject'] = 'Re: ' + self.subject
        msg['In-Reply-To'] = self.message.get("Message-ID")
        msg['References'] = self.message.get("Message-ID")
        msg.attach(MIMEText(response_body, 'plain'))
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Secure the connection
            server.login(self.user_email, self.user_passwrd)
            text = msg.as_string()
            server.sendmail(self.user_email, self.mail_from, text)
            server.quit()
            print('Email sent successfully.')
            self.mark_as_read()
        except Exception as e:
            print('Failed to send email. Error: ', str(e))
    def add_tag(self,tag):
        self.mail.store(self.id, '+X-GM-LABELS', tag)
        self.tags.append(tag)
    def mark_as_read(self):
        
        try:
            result, _ = self.mail.store(self.id, '+FLAGS', '\\Seen')
            if result != 'OK':
                print(f'Error marking email as read: {result}')
            else:
                print('Email marked as read.')
        except Exception as e:
            print(f'Exception occurred while marking email as read: {str(e)}')
    def save_to_file(self):
        counter = 1
        if not os.path.exists("emails"):
            os.mkdir("emails")
        filename = f"emails/{self.subject}.txt"
        
        while os.path.isfile(filename):
            filename = f"emails/{self.subject}_{counter}.txt"
            counter += 1

        with open(filename, "w") as file:
            file.write(self.body)
    def __eq__(self, __value: object) -> bool:
        if type(__value) == Mail:
            return (self.mail_from == __value.mail_from) and (self.subject == __value.subject)
        else:
            return False
    def __le__(self,other):
        return self < other
    def __ge__(self,other):
        return self > other
    def __lt__(self,other):
        if isinstance(other,Mail):
            return self.date<other.date
        else:
            return False
    def __gt__(self,other):
        if isinstance(other,Mail):
            return self.date>other.date
        else:
            return False   