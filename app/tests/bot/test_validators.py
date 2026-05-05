import pytest

from app.tg_bot.utils.validators import is_valid_domain


def test_valid_domains():
    assert is_valid_domain("google.com") is True
    assert is_valid_domain("scanme.nmap.org") is True
    assert is_valid_domain("my-custom-domain.io") is True

def test_invalid_domain():
    assert is_valid_domain("http://google.com") is False
    assert is_valid_domain("google.com/path") is False
    assert is_valid_domain("not_a_domain") is False
    assert is_valid_domain("1111") is False