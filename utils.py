import re


REGEX = re.compile(r"((https?://)?([\w-]+\.)+[a-z]{2,6})")


def parse_urls(text):
    return [x[0] for x in REGEX.findall(text)]


def list_to_string(it):
    s = ''
    for x in it:
        s += x + '\n'
    return s