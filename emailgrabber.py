import redis
import imaplib
import sys
import email

def process_pledge(subject,author,r):
    try:
        amount,group = subject.split()[1:]
        if amount.startswith('$'):
            amount = float(amount[1:])
        else:
            amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount pledged must be a positive number')
    except ValueError as e:
        #notify of idiocy
        print e
        return
    moneyleft = r.incrbyfloat(author+'.cash',-1*amount)
    if moneyleft<0:
        moneyleft = r.incrbyfloat(author+'.cash',amount)
        print "Can't give more money than you have!"
        #No, no, no
        return
    pledge = r.incrbyfloat('user.'+author+'.'+group,amount)
    r.sadd('group.'+group+'.backers',author)
    return

def process_unpledge(subject,author,r):
    try:
        amount,group = subject.split()[1:]
        if amount.startswith('$'):
            amount = float(amount[1:])
        else:
            amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount pledged must be a positive number')
    except ValueError as e:
        #notify of idiocy
        print e
        return
    #remove money from the pledge
    moneyleft = r.incrbyfloat('user.'+author+'.'+group,-1*amount)
    if moneyleft<0:
        moneyleft = r.incrbyfloat('user.'+author+'.'+group,amount)
        print "Can't give back more money than was pledged"
        #No, no, no
        return
    if moneyleft == 0:
        r.srem('group.'+group+'.backers',author)
    pledge = r.incrbyfloat(author+'.cash',amount)
    return

def process_buy(subject,author,r):
    try:
        group,tag,amount = subject.split()[1:]
        if amount.startswith('$'):
            amount = float(amount[1:])
        else:
            amount = float(amount)
        if amount <= 0:
            raise ValueError('Amount pledged must be a positive number')
    except ValueError as e:
        #notify of idiocy
        print e
        return
    # new proposal for purchase
    if tag not in r.sunion(group+'.purchases',group+'.proposals'):
        r.sadd('buy.'+group+'.'+tag,author)
        r.sadd(group+'.proposals',tag)
        r.set('cost.'+group+'.'+tag,amount)
    #someone came late to the party
    elif tag in r.smembers(group+'.purchases'):
        r.sadd('buy.'+group+'.'+tag,author)
    #people voting for the proposal
    elif tag in r.smembers(group+'.proposals'):
        r.sadd('buy.'+group+'.'+tag,author)
        #if we have a majority to buy, pull the trigger
        if r.scard('buy.'+group+'.'+tag) > (r.scard('group.'+group+'.backers')/2):
            try:
                r.smove(group+'.proposals',group+'.purchases',tag)
                pledgedcash = count_pledgemoney(group,r)
                usedcash = float(r.incrbyfloat('group.'+group+'.usedcash', \
                        float(r.get('cost.'+group+'.'+tag))))
                if (usedcash) > pledgedcash:
                    #what a dick
                    r.incrbyfloat('group.'+group+'.usedcash', \
                        -1*float(r.get('cost.'+group+'.'+tag)))
                    #need to notify of insufficient funds
                    print "Not enough money left in the bank to buy that!"
                    return
                #do puchasing stuff
            except:
                pass

def count_pledgemoney(group, r):
    pledgedcash = 0.0
    for user in r.smembers('group.'+group+'.backers'):
        pledgedcash += float(r.get('user.'+user+'.'+group))
    return pledgedcash

def main():
    credfile = open('credfile','r')
    USER,PASS,IMAP_SERVER,PORT_STRING = [x.strip() for x in credfile.readlines()]
    PORT = int(PORT_STRING)

    recv = imaplib.IMAP4_SSL(IMAP_SERVER,PORT)
    recv.login(USER,PASS)
    recv.select()

    r = redis.Redis()

    typ, data = recv.search(None, 'ALL')
    data_set = set(int(x) for x in data[0].split())
    r_set = set(int(x) for x in r.smembers('read'))
    toget = data_set - r_set
    for target in data_set:
        typ, data = recv.fetch(target, '(RFC822)')
        mail = data[0][1]
        message = email.message_from_string(mail)
        subject = message['Subject'].strip()
        author = message['From']
        if subject.startswith('PLEDGE'):
            process_pledge(subject,author,r)
        if subject.startswith('UNPLEDGE'):
            process_unpledge(subject,author,r)
        if subject.startswith('BUY'):
            process_buy(subject,author,r)
        r.sadd('read',target)

if __name__ == "__main__":
        main()
