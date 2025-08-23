# core/language.py
import configparser
import os
import sys
from core.config import LANGUAGE

_lang = configparser.ConfigParser()
lang_file = f"lang/{LANGUAGE}.ini"
if not os.path.exists(lang_file):
    print(f"❌ Language file not found: {lang_file}")
    sys.exit(1)

try:
    _lang.read(lang_file, encoding='utf-8')
except Exception as e:
    print(f"❌ Error reading language file {lang_file}: {e}")
    sys.exit(1)

def translate(key, **kwargs):
    """Translate and format a message."""
    text = _lang.get("lang", key, fallback=f"MISSING: {key}")
    return text.format(**kwargs)

