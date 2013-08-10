import redis
import imaplib
import sys
import email
import japan_parse

def process_pledge(subject,author):
    try:
        amount,group = subject.split()[1:]
        if amount.startswith('$'):
            amount = float(amount[1:])
        else:
            amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount pledged must be a positive number')
    except ValueError:
        #notify of idiocy
        return
    moneyleft = redis.incrbyfloat(author+'.cash',-1*amount)
    if moneyleft<0:
        moneyleft = redis.incrbyfloat(author+'.cash',amount)
        #No, no, no
        return
    pledge = redis.incrbyfloat(author+'.'+group,amount)
    redis.sadd('group.'+group+'.backers',author)
    return

def process_unpledge(subject,author):
    try:
        amount,group = subject.split()[1:]
        if amount.startswith('$'):
            amount = float(amount[1:])
        else:
            amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount pledged must be a positive number')
    except ValueError:
        #notify of idiocy
        return
    #remove money from the pledge
    moneyleft = redis.incrbyfloat(author+'.'+group,-1*amount)
    if moneyleft<0:
        moneyleft = redis.incrbyfloat(author+'.'+group,amount)
        #No, no, no
        return
    if moneyleft == 0:
        redis.srem('group.'+group+'.backers',author)
    pledge = redis.incrbyfloat(author+'.cash',amount)
    return

def process_buy(subject,author):
    try:
        group,tag,amount = subject.split()[1:]
        if amount.startswith('$'):
            amount = float(amount[1:])
        else:
            amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount pledged must be a positive number')
    except ValueError:
        #notify of idiocy
        return
    # new proposal for purchase
    if tag not in redis.sunion(group+'.purchases',group+'.proposals'):
        redis.sadd('buy.'+group+'.'+tag,author)
        redis.sadd(group+'.proposals',tag)
    #someone came late to the party
    elif tag in redis.smembers(group+'.purchases'):
        redis.sadd('buy.'+group+'.'+tag,author)
    #people voting for the proposal
    elif tag in redis.smembers(group+'.proposals'):
        redis.sadd('buy.'+group+'.'+tag,author)
        #if we have a majority to buy, pull the trigger
        if redis.scard('buy.'+group+'.'+tag) > (redis.scard('group.'+group+'.backers')/2):
            try:
                pledgedcash = 0.0
                for user in redis.smembers('group.'+group+'.backers'):
                    pledgedcash += float(redis.get('user.'+user+'.'+group))
                usedcash = float(redis.incrbyfloat('group.'+group+'.backers'+'.usedcash',amount))
                if (usedcash) > pledgedcash:
                    #what a dick
                    redis.incrbyfloat('group.'+group+'.backers'+'.usedcash',-1*amount)
                    #need to notify of insufficient funds
                    return
                redis.smove(group+'.proposals',group+'.purchases',tag)
                #do puchasing stuff
            except redis.exceptions.ResponseError:
                #someone is already doing that

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

