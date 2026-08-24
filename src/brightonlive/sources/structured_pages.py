from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup, Tag

from .base import AdapterResult
from .jsonld import EVENT_TYPES

LOCAL_TZ = ZoneInfo("Europe/London")
EVENT_LINK_MARKERS = ("event", "events", "whatson", "whats-on", "programme", "calendar", "tickets", "festival", "gig", "show")
MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}
MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_RE = re.compile(
    rf"(?:mon(?:day)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|fri(?:day)?|sat(?:urday)?|sun(?:day)?)?"
    rf"\s*(\d{{1,2}})(?:st|nd|rd|th)?(?:\s*[–-]\s*\d{{1,2}}(?:st|nd|rd|th)?)?\s+({MONTH_RE})"
    rf"(?:\s+(\d{{4}}))?(?:,?\s+(\d{{1,2}})[:.](\d{{2}})\s*(am|pm)?)?",
    re.I,
)
TIME_RE = re.compile(r"\b(\d{1,2})[:.](\d{2})\s*(am|pm)?\b", re.I)
BLOCKED_TITLES = {"home", "events", "tickets", "calendar", "search", "login", "my account", "about", "dates", "guide prices", "opening times"}


def _types(obj: dict) -> set[str]:
    value = obj.get("@type") or []
    return {value} if isinstance(value, str) else {str(x) for x in value}


def _event_from_jsonld(obj: dict, source: dict, page_url: str, now: str) -> dict | None:
    if not _types(obj).intersection(EVENT_TYPES):
        return None
    loc = obj.get("location") or {}
    if not isinstance(loc, dict):
        loc = {"name": str(loc or "")}
    addr = loc.get("address") or {}
    if not isinstance(addr, dict):
        addr = {}
    geo = loc.get("geo") or {}
    if not isinstance(geo, dict):
        geo = {}
    offers = obj.get("offers") or {}
    if isinstance(offers, list):
        offers = next((x for x in offers if isinstance(x, dict)), {})
    if not isinstance(offers, dict):
        offers = {}
    source_url = obj.get("url") or page_url
    return {
        "title": obj.get("name", ""),
        "description": obj.get("description", ""),
        "start": obj.get("startDate", ""),
        "end": obj.get("endDate", ""),
        "venue": loc.get("name") or source.get("default_venue") or source.get("name") or "",
        "address": addr.get("streetAddress", ""),
        "postcode": addr.get("postalCode") or source.get("default_postcode") or "",
        "latitude": geo.get("latitude") or source.get("latitude"),
        "longitude": geo.get("longitude") or source.get("longitude"),
        "category": source.get("default_category") or "Uncategorised",
        "website": source_url,
        "booking_url": offers.get("url", ""),
        "source_url": source_url,
        "source_owner": source.get("name") or urlparse(page_url).netloc,
        "manual_verified": False,
        "evidence": [{
            "source_key": source.get("key", "structured_pages"),
            "source_url": source_url,
            "source_owner": source.get("name") or urlparse(page_url).netloc,
            "source_type": source.get("source_type", "first_party"),
            "retrieved_at": now,
            "organisation_owned": True,
            "fields": ["title", "start", "end", "venue", "postcode", "website", "booking_url"],
        }],
    }


def _parse_datetime(text: str) -> datetime | None:
    match = DATE_RE.search(text)
    if not match:
        return None
    day, month_text, year_text, hour_text, minute_text, meridiem = match.groups()
    year = int(year_text or datetime.now(LOCAL_TZ).year)
    hour = int(hour_text or 0)
    minute = int(minute_text or 0)
    if hour_text is None:
        tm = TIME_RE.search(text)
        if tm:
            hour, minute, meridiem = int(tm.group(1)), int(tm.group(2)), tm.group(3)
    if meridiem:
        marker = meridiem.lower()
        if marker == "am" and hour == 12:
            hour = 0
        elif marker == "pm" and 1 <= hour < 12:
            hour += 12
    try:
        return datetime(year, MONTHS[month_text.lower()], int(day), hour, minute, tzinfo=LOCAL_TZ)
    except ValueError:
        return None


def _plausible_title(value: str) -> bool:
    clean = " ".join(value.split())
    return 3 <= len(clean) <= 120 and clean.lower().strip(" :") not in BLOCKED_TITLES


def _following_text(heading: Tag, max_parts: int = 5) -> str:
    parts: list[str] = []
    for sibling in heading.find_next_siblings():
        if not isinstance(sibling, Tag):
            continue
        if sibling.name in {"h2", "h3", "h4"} and parts:
            break
        text = sibling.get_text(" ", strip=True)
        if text:
            parts.append(text)
        if len(parts) >= max_parts:
            break
    return " ".join(parts)


def _preceding_date_text(heading: Tag, max_parts: int = 3) -> str:
    parts: list[str] = []
    for sibling in heading.find_previous_siblings():
        if not isinstance(sibling, Tag):
            continue
        text = sibling.get_text(" ", strip=True)
        if not text:
            continue
        if not DATE_RE.search(text) and not TIME_RE.search(text):
            break
        parts.append(text)
        if DATE_RE.search(text) or len(parts) >= max_parts:
            break
    parts.reverse()
    joined = " ".join(parts)
    return joined if DATE_RE.search(joined) else ""


def _visible_events(html: str, source: dict, page_url: str, now: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []
    for heading in soup.find_all(["h2", "h3", "h4"]):
        if not isinstance(heading, Tag):
            continue
        title = heading.get_text(" ", strip=True)
        if not _plausible_title(title):
            continue
        context = f"{title} {_following_text(heading)}"
        start = _parse_datetime(context)
        if start is None:
            context = f"{_preceding_date_text(heading)} {context}"
            start = _parse_datetime(context)
        if start is None:
            continue
        anchor = heading.find("a", href=True)
        event_url = urljoin(page_url, str(anchor["href"])) if anchor else page_url
        out.append({
            "title": title,
            "description": "",
            "start": start.isoformat(),
            "end": "",
            "venue": source.get("default_venue") or source.get("name") or "",
            "address": "",
            "postcode": source.get("default_postcode") or "",
            "latitude": source.get("latitude"),
            "longitude": source.get("longitude"),
            "category": source.get("default_category") or "Uncategorised",
            "website": event_url,
            "booking_url": "",
            "source_url": event_url,
            "source_owner": source.get("name") or urlparse(page_url).netloc,
            "manual_verified": False,
            "evidence": [{
                "source_key": source.get("key", "structured_pages"),
                "source_url": event_url,
                "source_owner": source.get("name") or urlparse(page_url).netloc,
                "source_type": source.get("source_type", "first_party"),
                "retrieved_at": now,
                "organisation_owned": True,
                "fields": ["title", "start", "venue", "website"],
            }],
        })
    return out


def _detail_links(html: str, source_url: str, max_links: int) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(source_url).netloc.lower()
    seen: set[str] = set()
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        if not href or href.startswith(("mailto:", "tel:", "#")):
            continue
        absolute = urljoin(source_url, href).split("#", 1)[0]
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != host:
            continue
        marker = f"{parsed.path.lower()} {anchor.get_text(' ', strip=True).lower()}"
        if not any(x in marker for x in EVENT_LINK_MARKERS):
            continue
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
        if len(links) >= max_links:
            break
    return links


def _fetch_page(url: str, timeout: int) -> tuple[str, str]:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "BrightonLive/0.2 structured-pages (+https://brightonlive.uk/)"},
    )
    response.raise_for_status()
    return response.text, str(response.url)


def _parse_page(html: str, page_url: str, source: dict, now: str) -> list[dict]:
    records = _visible_events(html, source, page_url, now)
    try:
        for obj in fetch_jsonld_from_html(html):
            event = _event_from_jsonld(obj, source, page_url, now)
            if event:
                records.append(event)
    except Exception:
        pass
    return records


def fetch_jsonld_from_html(html: str) -> list[dict]:
    """Parse JSON-LD without a second network request."""
    import json

    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            value = json.loads(tag.string or tag.get_text() or "{}")
        except json.JSONDecodeError:
            continue
        stack = value if isinstance(value, list) else [value]
        while stack:
            item = stack.pop(0)
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            if isinstance(graph, list):
                stack.extend(graph)
            else:
                out.append(item)
    return out


def harvest(sources: list[dict], timeout: int = 20, max_links_per_source: int = 30) -> AdapterResult:
    now = datetime.now(timezone.utc).isoformat()
    records: list[dict] = []
    failures: list[str] = []
    pages = 0
    for source in sources:
        url = str(source.get("url") or "").strip()
        if not url:
            continue
        try:
            html, final_url = _fetch_page(url, timeout)
            pages += 1
            records.extend(_parse_page(html, final_url, source, now))
            for link in _detail_links(html, final_url, max_links_per_source):
                if link == final_url:
                    continue
                try:
                    detail_html, detail_url = _fetch_page(link, timeout)
                    pages += 1
                    records.extend(_parse_page(detail_html, detail_url, source, now))
                except requests.RequestException as exc:
                    failures.append(f"{link}: {type(exc).__name__}: {exc}")
        except requests.RequestException as exc:
            failures.append(f"{url}: {type(exc).__name__}: {exc}")

    # Deterministic cross-parser de-duplication; the later event pipeline performs a
    # second, locality-aware merge and preserves independent evidence where appropriate.
    unique: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for row in records:
        key = (str(row.get("title") or "").casefold(), str(row.get("start") or ""), str(row.get("source_url") or ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    ok = bool(unique) or not failures
    return AdapterResult(
        "structured_pages",
        ok,
        unique,
        f"{len(unique)} event candidates from {pages} fetched page(s); {len(failures)} page failure(s)",
        {"pages_fetched": pages, "failures": failures[:50]},
    )
