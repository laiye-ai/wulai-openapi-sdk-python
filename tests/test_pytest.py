import pytest


@pytest.mark.parametrize('test_input,expected', [
    ('1+1', 2),
    ('2*10', 20),
    # ('1==1', False),
])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
