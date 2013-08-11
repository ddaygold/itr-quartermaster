import redis
import emailgrabber
'''
Requires py.test
'''

def setup():
    r = redis.Redis()
    r.flushdb()
    r.set('peter.cash',100)
    r.set('margaret.cash',100)
    r.set('bill.cash',100)
    r.set('kit.cash',100)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','kit',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','margaret',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','bill',r)

def teardown():
    r = redis.Redis()
    r.flushdb()

def test_negative():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $-1.00','peter',r)
    assert r.smembers('fenrir.proposals') == set()
    teardown()

def test_negative():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $-1.00','peter',r)
    assert r.smembers('fenrir.proposals') == set()
    teardown()

def test_add_proposal():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $1.00','peter',r)
    assert r.smembers('fenrir.proposals') == set(['wheels'])
    teardown()

def test_add_vote():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $1.00','peter',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','kit',r)
    assert r.smembers('fenrir.proposals') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 2
    teardown()

def test_win_cheap_vote():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $1.00','peter',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','kit',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret',r)
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 1.00
    teardown()

def test_win_expensive_vote():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $100.00','peter',r)
    emailgrabber.process_buy('BUY fenrir wheels $100.00','kit',r)
    emailgrabber.process_buy('BUY fenrir wheels $100.00','margaret',r)
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 0.00
    teardown()

def test_fail_mismatching_amounts():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $100.00','peter',r)
    emailgrabber.process_buy('BUY fenrir wheels $10.00','kit',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret',r)
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 0.00
    teardown()

def test_win_mismatching_amounts():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $40.0','peter',r)
    emailgrabber.process_buy('BUY fenrir wheels $10.00','kit',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret',r)
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 40.00
    teardown()

def test_late_to_the_party():
    r = redis.Redis()
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $40.0','peter',r)
    emailgrabber.process_buy('BUY fenrir wheels $10.00','kit',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret',r)
    emailgrabber.process_buy('BUY fenrir wheels $1.00','bill',r)
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 4
    assert float(r.get('group.fenrir.usedcash')) == 40.00
    teardown()
