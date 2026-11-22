"""Write the visible text of a saved HTML page.

Usage: python -I html2text.py <in.html> [<out.txt>]
Without out, prints to stdout as UTF-8.
"""
import html
import re
import sys


def visible_text(raw):
    s = raw
    m = re.search(r'<div itemprop="articleBody">(.*?)<footer', s, re.S)
    if m:
        s = m.group(1)
    else:
        m = re.search(r"<body[^>]*>(.*)</body>", s, re.S | re.I)
        if m:
            s = m.group(1)
    s = re.sub(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<(br|/p|/div|/li|/tr|/h[1-6]|/table|/section)[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<t[dh][^>]*>", " | ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("", "")
    s = re.sub(r"[ \t\r\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip() + "\n"


def main():
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        t = visible_text(f.read())
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    else:
        sys.stdout.buffer.write(t.encode("utf-8"))


if __name__ == "__main__":
    main()
