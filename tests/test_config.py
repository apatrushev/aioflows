from aioflows.simple import List, Logger, Null


def test_options():
    assert Null().options == ()


def test_list():
    options = List().options
    assert len(options) == 1
    props = options[0]['$defs']['Options']['properties']
    assert len(props) == 1
    assert props['data']['type'] == 'array'


def test_complex():
    options = (List() >> Logger() >> Null()).options
    assert len(options) == 2
    props = [[*o['$defs']['Options']['properties'].keys()] for o in options]
    assert props == [['data'], ['logger', 'level']]


def test_default():
    options = Logger(logger='test').options
    props = options[0]['$defs']['Options']['properties']
    assert props['logger']['default'] == 'test'
