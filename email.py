import redis
import imaplib
import sys

credfile = open('credfile','r')
USER,PASS,IMAP_SERVER,PORT_STRING = [x.strip() for x in credfile.readlines()]
PORT = int(PORT_STRING)

recv = imaplib.IMAP4_SSL(IMAP_SERVER,PORT)
recv.login(USER,PASS)
recv.select()

redis = redis.Redis()

typ, data = recv.search(None, 'ALL')
data_set = set(int(x) for x in data[0].split())
redis_set = redis.smembers('read')
toget = data_set - redis_set
for target in toget:
        typ, data = recv.fetch(target, '(RFC822)')
        redis.set('mail:'+str(target),data)
        redis.sadd('read',target)
