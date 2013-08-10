import redis
import imaplib
import sys
import email
import japan_parse

def process_pledge(subject,author):
    tagname,amount,group = subject.split()
    if amount.startswith('$'):
        amount = float(amount[1:])
    else:
        amount = float(amount)
    moneyleft = redis.incrbyfloat(author+'.cash',-1*amount)
    if moneyleft<0:
        moneyleft = redis.incrbyfloat(author+'.cash',amount)
        #No, no, no
        return
    pledge = redis.incrbyfloat(author+'.'+group,amount)
    redis.sadd('group.'+group,author)
    return

def process_unpledge(subject,author):
    tagname,amount,group = subject.split()
    if amount.startswith('$'):
        amount = float(amount[1:])
    else:
        amount = float(amount)
    moneyleft = redis.incrbyfloat(author+'.'+group,-1*amount)
    if moneyleft<0:
        moneyleft = redis.incrbyfloat(author+'.'+group,amount)
        #No, no, no
        return
    if moneleft == 0:
        redis.srem('group.'+group,author)
    pledge = redis.incrbyfloat(author+'.cash',amount)
    return

def process_buy(subject,author):
    command,tag,amount
    if amount.startswith('$'):
        amount = float(amount[1:])
    else:
        amount = float(amount)
    pass

credfile = open('credfile','r')
USER,PASS,IMAP_SERVER,PORT_STRING = [x.strip() for x in credfile.readlines()]
PORT = int(PORT_STRING)

recv = imaplib.IMAP4_SSL(IMAP_SERVER,PORT)
recv.login(USER,PASS)
recv.select()

redis = redis.Redis()

typ, data = recv.search(None, 'ALL')
data_set = set(int(x) for x in data[0].split())
redis_set = set(int(x) for x in redis.smembers('read'))
toget = data_set - redis_set
for target in data_set:
    typ, data = recv.fetch(target, '(RFC822)')
    mail = data[0][1]
    message = email.message_from_string(mail)
    subject = message['Subject'].strip()
    author = message['From']
    if subject.startswith('PLEDGE'):
        process_pledge(subject,author)
    if subject.startswith('UNPLEDGE'):
        process_unpledge(subject,author)
    if subject.startswith('BUY'):
        process_buy(subject,author)
    redis.sadd('read',target)



#    print type(data), len(data)
#    print type(data[0]), data[0][1]
#    redis.set('mail:'+str(target),data[0][1])
#    redis.sadd('read',target)

