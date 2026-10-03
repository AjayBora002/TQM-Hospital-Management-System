"""
validators.py -- Shared validation rules (Q07 support).
Centralizing validation prevents each view from re-implementing (and
potentially mis-implementing) the same accuracy rules.
"""
import re


def is_valid_date(value):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value.strip()))


def is_valid_time(value):
    return bool(re.match(r"^([01]\d|2[0-3]):[0-5]\d$", value.strip()))


def is_valid_phone_digits(digits):
    return len(digits) == 10


def not_empty(value):
    return bool(value and value.strip())


def in_fixed_set(value, allowed):
    return value in allowed
