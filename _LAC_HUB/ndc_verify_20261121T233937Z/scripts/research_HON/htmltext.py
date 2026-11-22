"""Print or save the visible text and the links of a saved HTML page.

Usage: python -I htmltext.py <html file> [--links] [--out <txt file>] [--max N]
The HTML file is untrusted data; it is only parsed as text.
"""
import html
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def visible_text(raw):
    t = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", raw)
    t = re.sub(r"(?is)<!--.*?-->", " ", t)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|td|th|section|article|table|ul|ol|dt|dd)>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    lines = [re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in t.split("\n")]
    out = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip() + "\n"


def main():
    args = sys.argv[1:]
    path = args[0]
    raw = open(path, encoding="utf-8", errors="replace").read()
    if "--links" in args:
        for h in sorted(set(re.findall(r'href=["\']([^"\'#]+)["\']', raw))):
            print(h)
        return
    txt = visible_text(raw)
    if "--out" in args:
        out = args[args.index("--out") + 1]
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        print("wrote", out, len(txt))
        return
    mx = int(args[args.index("--max") + 1]) if "--max" in args else 6000
    print(txt[:mx])


if __name__ == "__main__":
    main()
