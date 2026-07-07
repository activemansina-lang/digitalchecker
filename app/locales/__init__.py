from __future__ import annotations

from app.locales import en, fa

_LOCALES = {"fa": fa.STRINGS, "en": en.STRINGS}


def t(language: str, key: str, **kwargs) -> str:
    strings = _LOCALES.get(language, _LOCALES["fa"])
    template = strings.get(key, key)
    return template.format(**kwargs) if kwargs else template


def button(language: str, key: str) -> str:
    strings = _LOCALES.get(language, _LOCALES["fa"])
    return strings["buttons"].get(key, key)
