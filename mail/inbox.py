import email,imaplib
from .mail import Mail
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
    def change_inbox(self,desired_inbox):
        self.desired_inbox = desired_inbox
        self.mail.select(self.desired_inbox)
    def fetch_mail(self,criteria="UNSEEN"):
        res = self.mail.search(None, criteria)
        self.mails = {}
        for item in res[1][0].split():
            self.mails[item] = Mail(self.mail,item,self.email,self.password)
    def fetch_tags(self):
        def add_to_dict(dictonary,key):
            dictonary[key]={"enabled":False}
        dictionary = {}
        lst = []
        for a in self.mail.list()[1]:
            string = a.decode("utf-8")
            string = string.split('"')
            lst.append(string[-2])

        for a in lst:
            data = a.split("/")
            prev = dictionary
            for val in data:
                if val not in prev:
                    add_to_dict(prev,val)
                prev = prev[val]

        return dictionary
        
    