import redis
import imaplib
import sys
import email
import japan_parse

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
    message = japan_parse.parse(mail)
    print message
#    print type(data), len(data)
#    print type(data[0]), data[0][1]
#    redis.set('mail:'+str(target),data[0][1])
#    redis.sadd('read',target)

