#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import random
import re

from yandex_translate import *

from commonscript import getEncoding
from configurer import API_YANDEX_KEY


GL_LANGUAGES = [
    ["ru", "rus"],
    ["en", "eng"],
    ["pl", "pol"],
    ["uk", "ukr"],
    ["de", "deu"],
    ["fr", "fra"],
    ["es", "esl"],
    ["it", "ita"],
    ["bg", "bul"],
    ["cs", "ces"],
    ["tr", "tur"],
    ["ro", "rum"],
    ["sr", "sr"]
]


def detect(path, encoding=None):
    translate = YandexTranslate(API_YANDEX_KEY)

    n = 10
    m = 50
    fragments = getNfragmentsTextbyMletters(path, n, m, encoding)
    results = {"rus": 0, "eng": 0, "pol": 0, "ukr": 0, "deu": 0, "fra": 0, "esl": 0, "ita": 0, "bul": 0, "ces": 0,
               "tur": 0, "rum": 0, "sr": 0, "unknown": 0}

    for fragment in fragments:
        try:
            textlanguage = translate.detect(fragment)
            for Pair in GL_LANGUAGES:
                if Pair[0] == textlanguage:
                    # print Pair[1]
                    results[Pair[1]] += 1
                    break
        except YandexTranslateException as e:
            print e

    max = results['eng']
    max2 = 'unknown'
    for elem in results:
        if results[elem] >= max:
            max = results[elem]
            max2 = elem

    return max2


def getNfragmentsTextbyMletters(path, n, m, encoding):
    if encoding is None:
        encoding = getEncoding(path)
    file = open(path, 'r')
    str = file.read().decode(encoding).encode('utf_8').strip()
    file.close()
    rtext = []
    i = 0
    p = re.compile(r'<.*?>')
    str = p.sub('', str)
    while i < n:
        value = random.randint(0, len(str))
        text = str[value: value + m]
        if text:
            rtext.append(text)
            i += 1
    return rtext
