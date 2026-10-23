"""
helpers.py -- Shared serialization helpers for API responses
"""
import sqlite3

def row_to_dict(row):
    if row is None:
        return None
    try:
        return dict(row)
    except (TypeError, ValueError):
        return {}

def rows_to_list(rows):
    if not rows:
        return []
    result = []
    for r in rows:
        if r is not None:
            try:
                result.append(dict(r))
            except (TypeError, ValueError):
                continue
    return result
