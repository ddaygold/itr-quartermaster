import redis
import emailgrabber
'''
Requires py.test
'''

r = redis.Redis()
def setup():
    r.flushdb()
    r.set('peter.cash',100)
    r.set('margaret.cash',100)
    r.set('bill.cash',100)
    r.set('kit.cash',100)
    r.set('testing','TRUE')
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter')
    emailgrabber.process_pledge('PLEDGE $10 fenrir','kit')
    emailgrabber.process_pledge('PLEDGE $10 fenrir','margaret')
    emailgrabber.process_pledge('PLEDGE $10 fenrir','bill')

def teardown():
    r.flushdb()

def test_negative():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $-1.00','peter')
    assert r.smembers('fenrir.proposals') == set()
    teardown()

def test_add_proposal():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $1.00','peter')
    assert r.smembers('fenrir.proposals') == set(['wheels'])
    teardown()

def test_add_vote():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $1.00','peter')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','kit')
    assert r.smembers('fenrir.proposals') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 2
    teardown()

def test_win_cheap_vote():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $1.00','peter')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','kit')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret')
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 1.00
    teardown()

def test_win_expensive_vote():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $100.00','peter')
    emailgrabber.process_buy('BUY fenrir wheels $100.00','kit')
    emailgrabber.process_buy('BUY fenrir wheels $100.00','margaret')
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 0.00
    teardown()

def test_fail_mismatching_amounts():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $100.00','peter')
    emailgrabber.process_buy('BUY fenrir wheels $10.00','kit')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret')
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 0.00
    teardown()

def test_win_mismatching_amounts():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $40.0','peter')
    emailgrabber.process_buy('BUY fenrir wheels $10.00','kit')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret')
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 3
    assert float(r.get('group.fenrir.usedcash')) == 40.00
    teardown()

def test_late_to_the_party():
    setup()
    emailgrabber.process_buy('BUY fenrir wheels $40.0','peter')
    emailgrabber.process_buy('BUY fenrir wheels $10.00','kit')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','margaret')
    emailgrabber.process_buy('BUY fenrir wheels $1.00','bill')
    assert r.smembers('fenrir.proposals') == set()
    assert r.smembers('fenrir.purchases') == set(['wheels'])
    assert r.scard('buy.fenrir.wheels') == 4
    assert float(r.get('group.fenrir.usedcash')) == 40.00
    teardown()
