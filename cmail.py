import smtplib
from smtplib import SMTP
from email.message import EmailMessage
def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('snskalyan2002@gmail.com',"nybd uqnx eoec mzyv")
    msg=EmailMessage()
    msg['FROM']='snskalyan2002@gmail.com'
    msg['SUBJECT']=subject
    msg['To']=to
    msg.set_content(body)
    server.send_message(msg)
    server.quit() 