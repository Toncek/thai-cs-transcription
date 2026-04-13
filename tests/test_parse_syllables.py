import pytest
from src.transcriber import parse_syllables

def test_parse_syllables_basic():
    """Test simple Consonant + Vowel patterns."""
    assert parse_syllables("กา") == ["กา"]
    assert parse_syllables("ดี") == ["ดี"]
    assert parse_syllables("ปู") == ["ปู"]

def test_parse_syllables_leading_vowel():
    """Test patterns starting with a leading vowel."""
    assert parse_syllables("ไป") == ["ไป"]
    assert parse_syllables("เมา") == ["เมา"]
    assert parse_syllables("แก") == ["แก"]

def test_parse_syllables_final_consonant():
    """Test syllables with final consonants."""
    assert parse_syllables("กิน") == ["กิน"]
    assert parse_syllables("เดิน") == ["เดิน"]
    assert parse_syllables("เรียน") == ["เรียน"]

def test_parse_syllables_clusters():
    """Test consonant clusters."""
    assert parse_syllables("ปลา") == ["ปลา"]
    assert parse_syllables("กวาง") == ["กวาง"]
    assert parse_syllables("ครับ") == ["ครับ"]

def test_parse_syllables_tone_marks():
    """Test syllables with tone marks."""
    assert parse_syllables("บ้าน") == ["บ้าน"]
    assert parse_syllables("แม่") == ["แม่"]
    assert parse_syllables("ได้") == ["ได้"]

def test_parse_syllables_multi_syllable():
    """Test multi-syllable words."""
    assert parse_syllables("กาแฟ") == ["กา", "แฟ"]
    assert parse_syllables("โรงเรียน") == ["โรง", "เรียน"]
    assert parse_syllables("สวัสดี") == ["ส", "วัส", "ดี"]

def test_parse_syllables_non_thai():
    """Test with non-Thai characters."""
    assert parse_syllables("123") == ["1", "2", "3"]
    assert parse_syllables("Hello") == ["H", "e", "l", "l", "o"]

def test_parse_syllables_silent_mark():
    """Test syllables with silent marks (Garan)."""
    # Trace for การ์:
    # 1. ก (Initial)
    # 2. า (Following)
    # 3. ร is not added as final because next char is ์ (not consonant or leading vowel)
    # 4. Next syllable starts with ร, then ์ is added as following/silent.
    assert parse_syllables("การ์") == ["กา", "ร์"]
