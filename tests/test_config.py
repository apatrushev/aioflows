from aioflows.simple import Counter, List, Logger, Null, Ticker


def test_options():
    assert Null().options == ()


def test_list():
    options = List().options
    assert len(options) == 1
    props = options[0]['definitions']['Options']['properties']
    assert len(props) == 1
    assert props['data']['type'] == 'array'


def test_complex():
    options = (List() >> Logger() >> Null()).options
    assert len(options) == 2
    props = [[*o['definitions']['Options']['properties'].keys()] for o in options]
    assert props == [['data'], ['logger', 'level']]


def test_default():
    options = Logger(logger='test').options
    props = options[0]['definitions']['Options']['properties']
    assert props['logger']['default'] == 'test'


def test_configure():
    flow = (Ticker() >> Counter() >> Logger() >> Null())
    flow.configure([{'limit': 100}, {'logger': 'test'}])
    options = flow.options
    props = options[0]['definitions']['Options']['properties']
    assert props['limit']['default'] == 100
    props = options[1]['definitions']['Options']['properties']
    assert props['logger']['default'] == 'test'
