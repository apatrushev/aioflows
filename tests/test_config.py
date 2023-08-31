from aioflows.simple import Counter, List, Logger, Null, Ticker


def test_options_null():
    assert Null().options == ()


def test_options_list():
    options = List().options
    assert len(options) == 1
    props = options[0]['properties']
    assert len(props) == 1
    assert props['data']['type'] == 'array'


def test_options_complex():
    options = (List() >> Logger() >> Null()).options
    assert len(options) == 2
    props = [[*o['properties'].keys()] for o in options]
    assert props == [['data'], ['logger', 'level']]


def test_options_default():
    options = Logger(logger='test').options
    props = options[0]['properties']
    assert props['logger']['default'] == 'test'


def test_options_configure():
    flow = (Ticker() >> Counter() >> Logger() >> Null())
    flow.configure([{'limit': 100}, {'logger': 'test'}])
    options = flow.options
    props = options[0]['properties']
    assert props['limit']['default'] == 100
    props = options[1]['properties']
    assert props['logger']['default'] == 'test'
