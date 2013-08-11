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

def teardown():
    r = redis.Redis()
    r.flushdb()

def test_negative():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $-1.00 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 100.00
    teardown()

def test_too_big():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $10000 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 100.00
    teardown()

def test_succeed():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 90.00
    teardown()

def test_succeed_then_fail():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 90.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 80.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 70.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 60.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 50.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 40.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 30.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 20.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 10.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 0.00
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    assert float(r.get('peter.cash')) == 0.00
    teardown()

def test_pledge_group_building():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','margaret',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','bill',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','kit',r)
    assert r.smembers('group.fenrir.backers') == \
        set(['peter','bill','margaret','kit'])
    teardown()

def test_money_count():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','margaret',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','bill',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','kit',r)
    assert emailgrabber.count_pledgemoney('fenrir',r) == 40.00
    teardown()

def test_unpledge():
    r = redis.Redis()
    setup()
    emailgrabber.process_pledge('PLEDGE $10 fenrir','peter',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','margaret',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','bill',r)
    emailgrabber.process_pledge('PLEDGE $10 fenrir','kit',r)
    emailgrabber.process_unpledge('UNPLEDGE $5 fenrir','kit',r)
    assert emailgrabber.count_pledgemoney('fenrir',r) == 35.00
    assert float(r.get('kit.cash')) == 95.00
    assert r.smembers('group.fenrir.backers') == \
        set(['peter','bill','margaret','kit'])
    emailgrabber.process_unpledge('UNPLEDGE $-5 fenrir','kit',r)
    assert emailgrabber.count_pledgemoney('fenrir',r) == 35.00
    assert float(r.get('kit.cash')) == 95.00
    assert r.smembers('group.fenrir.backers') == \
        set(['peter','bill','margaret','kit'])
    emailgrabber.process_unpledge('UNPLEDGE $5 fenrir','kit',r)
    assert emailgrabber.count_pledgemoney('fenrir',r) == 30.00
    assert float(r.get('kit.cash')) == 100.00
    assert r.smembers('group.fenrir.backers') == \
        set(['peter','bill','margaret'])
    emailgrabber.process_unpledge('UNPLEDGE $5 fenrir','kit',r)
    assert emailgrabber.count_pledgemoney('fenrir',r) == 30.00
    assert float(r.get('kit.cash')) == 100.00
    assert r.smembers('group.fenrir.backers') == \
        set(['peter','bill','margaret'])
    teardown()
