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


def flatten_urls(payload):
    urls = set()
    for sec in payload.get("sections", []):
        for item in sec.get("items", []):
            u = item.get("url")
            if u:
                urls.add(u)
    return urls


def flatten_items(payload):
    out = []
    for sec in payload.get("sections", []):
        for item in sec.get("items", []):
            out.append({
                "section": sec.get("title", ""),
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "published": item.get("published", ""),
            })
    return out


def load_previous_payload():
    try:
        with open("data/latest.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def build_changes(previous, current):
    if not previous:
        return {
            "previousUpdated": None,
            "newCount": 0,
            "removedCount": 0,
            "newItems": [],
            "summary": "First run: baseline captured. Changes will appear from tomorrow.",
        }

    prev_urls = flatten_urls(previous)
    curr_items = flatten_items(current)
    curr_urls = {i["url"] for i in curr_items if i.get("url")}

    new_items = [i for i in curr_items if i.get("url") and i["url"] not in prev_urls]
    removed_count = len([u for u in prev_urls if u not in curr_urls])

    return {
        "previousUpdated": previous.get("updated"),
        "newCount": len(new_items),
        "removedCount": removed_count,
        "newItems": new_items[:12],
        "summary": (
            "No material change since yesterday."
            if len(new_items) == 0 and removed_count == 0
            else f"{len(new_items)} new item(s), {removed_count} removed item(s) since last update."
        ),
    }


def main():
    previous = load_previous_payload()
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
    payload["changes"] = build_changes(previous, payload)

    with open("data/latest.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
