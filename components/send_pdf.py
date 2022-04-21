import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from email.mime.base import MIMEBase
from email import encoders

def get_settings(item):
    with open("components/settings.json") as f:
        settings = json.load(f)
        return settings[item]


def send_email(attachment):
    host = "smtp.gmail.com"
    port = '587'
    login = get_settings("login")
    password = get_settings("password")
    to = get_settings("to_email")
    to = "davidhioner@gmail.com"

    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.login(login, password)

    # separete filename from path
    filename = attachment.split('/')[-1]
    name = filename.split('.')[0]
    name.replace('CRE_', '')

    # create email
    body = """
    <p>Hi,</p>
    <p>this is an automatic message!</p>
    <p>Created by: <b>David Ioner</b></p>
    <p>
    """

    mail_msg = MIMEMultipart()
    mail_msg['From'] = login
    mail_msg['To'] = to
    mail_msg['Subject'] = f'{name} contract'
    mail_msg.attach(MIMEText(body, 'html'))

    # get full path to attachment
    
    attach = open(attachment, 'rb')

    att = MIMEBase('application', 'octet-stream')
    att.set_payload(attach.read())
    encoders.encode_base64(att)


    
    att.add_header('Content-Disposition', 'attachment', filename=filename)
    attach.close()
    mail_msg.attach(att)

    #send email
    server.sendmail(mail_msg['From'], mail_msg['To'], mail_msg.as_string())
    server.quit()

