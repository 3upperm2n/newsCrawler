#!/usr/bin/env python

import feedparser
from urlparse import urlparse
import re

import time
from subprocess import check_output

import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')


# email
import getpass
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

rss_dd = {}
rss_dd['stock_market'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=stock+market&output=rss'
rss_dd['nvidia'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=nvidia&output=rss'
rss_dd['amd'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=amd&output=rss'
rss_dd['samsung'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=samsung&output=rss'
rss_dd['intel'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=intel&output=rss'
rss_dd['qualcomm'] ='https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=qualcomm&output=rss'
rss_dd['amazon'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=amazon&output=rss'
rss_dd['microsoft'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=microsoft&output=rss'
rss_dd['facebook'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=facebook&output=rss'
rss_dd['alibaba'] = 'https://news.google.com/news?cf=all&hl=en&pz=1&ned=us&q=alibaba&output=rss'

#
# function to get the current time
#
current_time_millis = lambda: int(round(time.time() * 1000))
current_timestamp = current_time_millis()
#print current_timestamp

gmail_user = 'ylm.neu@gmail.com'
gmail_pwd = 'r9bbtzhy'

# database
db = 'feeds.db'

# time limit : 24 hours
limit = 24 * 3600 * 1000  


def post_is_in_db(title):
    with open(db, 'r') as database:
        for line in database:
            if title in line:
                return True
    return False


# return true if the title is in the database with a timestamp > limit
def post_is_in_db_with_old_timestamp(title):

    with open(db, 'r') as database:
        for line in database:
            if title in line:
                ts_as_string = line.split('|', 1)[1]
                ts = long(ts_as_string)
                if current_timestamp - ts > limit:
                    return True


def mail(to, subject, text, attach=None):
    global gmail_user, gmail_pwd
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    if attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    mailServer.close()
    return False


def email_feed(email_title, posts_to_print):
    # input: a list of dd ['title', 'description']
    send_msg = ''
    
    for post in posts_to_print:
        my_tit = post['title']
        my_des = post['description']
        send_msg += '\n=>' + my_tit + '\n'
        
    try:
        mail("leimingyu830@gmail.com", email_title, send_msg)
        #pass
    except:
        sys.stderr.write('Something went wrong...')


def process_url(groupname, url):

    #posts_to_skip = []
    posts_to_print = [] # a list of dd
    
    feed = feedparser.parse(url)

    NewFeed = False
    for post in feed.entries:
        title = post.title
        title_encode = title.encode('utf-8') 
        
        # within 24 hours
        if not post_is_in_db_with_old_timestamp(title_encode):
            #url = urlparse(post.link)
            description = re.compile(r'<.*?>').sub('', post["description"])
            postinfo_dd = {'title':title, 'description': description}
            posts_to_print.append(postinfo_dd)
            NewFeed = True
    
    #print(len(posts_to_print))
    posts_to_email = []
    
    if NewFeed:
        # store
        #print('new feed')
        
        f = open(db, 'a')
        for item in posts_to_print:
            tit = item['title']
            des = item['description']
            
            tit_encode = tit.encode('utf-8')
            des_encode = des.encode('utf-8')
            
            # the post is new
            if not post_is_in_db(tit_encode):
                f.write(tit_encode + "|" + str(current_timestamp) + "\n")
                posts_to_email.append({'title':tit_encode, 'description': des_encode})
                
        f.close
        
        if posts_to_email:
            email_feed(groupname, posts_to_email)
                       

def run_rss(rss_dd):
    for key, value in rss_dd.items():
        # groupname , url
        process_url(key, value)



### main
run_rss(rss_dd)
