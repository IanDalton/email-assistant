import email,imaplib
from mail import Mail
class Inbox():
    def __init__(self,email,password,mail_host,desired_inbox):
        self.email = email
        self.password = password
        self.mail_host = mail_host
        self.desired_inbox = desired_inbox
        self.mail = imaplib.IMAP4_SSL(self.mail_host)
        self.login()
        self.mails = {}
    def login(self):
        self.mail.login(self.email,self.password)
        self.mail.select(self.desired_inbox)
    def fetch_mail(self,criteria="UNSEEN"):
        res = self.mail.search(None, criteria)
        for item in res[1][0].split():
            self.mails[item] = Mail(self.mail,item)
    
        
    