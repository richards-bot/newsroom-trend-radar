#!/usr/bin/env python3
import json
import datetime as dt
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

MAX_PER_SOURCE = 5
UA = "newsroom-trend-radar/1.0"

SECTIONS = {
    "Vendor Watch: iconik / LucidLink / Backlight": [
        ("iconik changelog", "https://help.iconik.backlight.co/hc/en-us/articles/25304685702167-Iconik-Web-Changelog"),
        ("LucidLink release notes", "https://support.lucidlink.com/hc/en-us/sections/31125638256269-Release-notes"),
        ("Backlight news", "https://www.backlight.co/feed"),
    ],
    "Multimedia + Video Strategy": [
        ("Nieman Lab", "https://www.niemanlab.org/feed/"),
        ("Digiday", "https://digiday.com/feed/"),
        ("YouTube Official Blog", "https://blog.youtube/feed/"),
    ],
    "AI for Newsrooms & Production": [
        ("OpenAI news", "https://openai.com/news/rss.xml"),
        ("Google DeepMind blog", "https://deepmind.google/blog/rss.xml"),
        ("Anthropic news", "https://www.anthropic.com/news/rss.xml"),
    ],
    "Social Distribution Platforms": [
        ("TikTok newsroom", "https://newsroom.tiktok.com/en-us/rss"),
        ("Meta newsroom", "https://about.fb.com/news/feed/"),
        ("Instagram creators", "https://creators.instagram.com/blog/rss/"),
    ],
}


def fetch(url):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=20) as r:
        return r.read()


def _tag_name(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag


def parse_rss(data):
    out = []
    root = ET.fromstring(data)

    # RSS <item>
    for item in root.findall('.//item'):
        title = (item.findtext('title') or 'Untitled').strip()
        link = (item.findtext('link') or '').strip()
        pub = (item.findtext('pubDate') or item.findtext('published') or '').strip()
        if link:
            out.append({'title': title, 'url': link, 'published': pub})
        if len(out) >= MAX_PER_SOURCE:
            return out

    # Atom <entry>
    for entry in root.findall('.//{*}entry'):
        title = (entry.findtext('{*}title') or 'Untitled').strip()
        pub = (entry.findtext('{*}updated') or entry.findtext('{*}published') or '').strip()
        link = ''
        for child in entry:
            if _tag_name(child.tag) == 'link':
                href = child.attrib.get('href', '').strip()
                rel = child.attrib.get('rel', 'alternate')
                if href and rel in ('alternate', ''):
                    link = href
                    break
        if link:
            out.append({'title': title, 'url': link, 'published': pub})
        if len(out) >= MAX_PER_SOURCE:
            return out

    return out


def fallback_page(label, url):
    return [{"title": f"Open source page: {label}", "url": url, "published": ""}]


def main():
    sections = []
    total = 0
    src_count = 0
    for section, sources in SECTIONS.items():
        items = []
        for label, url in sources:
            src_count += 1
            try:
                if url.endswith(".xml") or "feed" in url or url.endswith("/"):
                    raw = fetch(url)
                    parsed = parse_rss(raw)
                    if parsed:
                        for p in parsed:
                            p["source"] = label
                        items.extend(parsed)
                    else:
                        items.extend([{**x, "source": label} for x in fallback_page(label, url)])
                else:
                    items.extend([{**x, "source": label} for x in fallback_page(label, url)])
            except Exception:
                items.extend([{**x, "source": label} for x in fallback_page(label, url)])
        total += len(items)
        sections.append({"title": section, "items": items[:15]})

    payload = {
        "updated": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        "meta": {"totalSources": src_count, "totalItems": total},
        "sections": sections,
    }

    with open("data/latest.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
