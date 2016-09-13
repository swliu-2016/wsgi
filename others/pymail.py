#!/usr/bin/env python
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.header import Header
import time

def sendIPmail(ipaddr):
   sender = 'liu@somewhere'
   receiver = 'w@elsewhere'
   subject = 'Raspberry Server IP'
   smtpserver = 'mailserver'
   username = 'liusiw'
   password = '****'

   msg = MIMEText(ipaddr ,_subtype='text', _charset='utf-8')
   msg['Subject'] = Header(subject, 'utf-8')
   msg['from']    = 'from'
   msg['to']      = 'to'

   smtp = smtplib.SMTP()
   smtp.connect('mail.sysu.edu.cn')
   smtp.login(username, password)
   smtp.sendmail(sender, receiver, msg.as_string())
   smtp.quit()

def writeIP(ipaddr):
   outfile = open("/srv/http/ip.txt", "w")
   outfile.write(ipaddr)
   outfile.close()
   
# Get the public IP now
p = subprocess.Popen(["curl","-s", "ident.me"], stdout=subprocess.PIPE)
ipinfo = b''.join(p.stdout.readlines())
ip = ipinfo.decode()
ip=ip.replace('[', '')
ip=ip.replace(']', '')
ip=ip.lstrip()
ip=ip.rstrip()
ipnowstr=ip
ip=ip.replace('.', '')
ipnow=int(ip)

# Get the obtained IP before
infile = open("/srv/http/ip.txt", "r")
ipbeforestr = infile.readline()
infile.close()
ipsplit = ipbeforestr.split('.')
ipbefore = int(''.join(ipsplit))

# Compared the IP Address
if ipnow != ipbefore:
   writeIP(ipnowstr)
   sendIPmail(ipnowstr)
else:
   print(ipnowstr)
