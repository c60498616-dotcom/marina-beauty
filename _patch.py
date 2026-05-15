"""One-shot patcher for МАРИНА БЬЮТИ static site.
Injects animations.css / scripts.js into <head>, rewires nav <a href="#">
links by anchor text, wires "Забронировать" buttons to booking.html and
sprinkles data-reveal / motion utility classes on key sections.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).parent
FILES = ["index.html", "gallery.html", "price.html", "booking.html"]

# anchor-text -> route
ROUTES = {
    "Главная": "index.html",
    "Услуги": "price.html",
    "Галерея": "gallery.html",
    "Запись": "booking.html",
    "Прайс-лист": "price.html",
    "О салоне": "index.html",
    "Мастера": "index.html",
    "Контакты": "booking.html",
}

HEAD_INJECT = (
    '<link href="assets/animations.css" rel="stylesheet"/>\n'
    '<script defer src="assets/scripts.js"></script>\n'
    "</head>"
)


def patch_anchor(match: re.Match) -> str:
    attrs = match.group(1)
    inner = match.group(2)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", inner)).strip()
    route = ROUTES.get(text)
    if not route:
        return match.group(0)
    # set href
    if 'href="#"' in attrs:
        attrs = attrs.replace('href="#"', f'href="{route}"')
    else:
        attrs = re.sub(r'href="[^"]*"', f'href="{route}"', attrs)
    # add data-route + nav-link class
    if "data-route=" not in attrs:
        attrs += f' data-route="{route}"'
    attrs = re.sub(r'class="([^"]*)"', lambda m: f'class="{m.group(1)} nav-link"', attrs, count=1)
    return f"<a{attrs}>{inner}</a>"


# regex for single-line anchors
A_RE = re.compile(r"<a([^>]*)>(.*?)</a>", re.DOTALL)


def rewire_booking_buttons(html: str) -> str:
    """Convert <button ...>Забронировать[ визит]</button> into <a> linking to booking.html."""

    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        inner = m.group(2)
        text = re.sub(r"\s+", " ", inner).strip()
        if text in {"Забронировать", "Забронировать визит", "Онлайн запись"}:
            attrs = re.sub(r'class="([^"]*)"', lambda x: f'class="{x.group(1)} btn-shimmer inline-block"', attrs, count=1)
            return f'<a href="booking.html" data-route="booking.html"{attrs}>{inner}</a>'
        return m.group(0)

    return re.sub(r"<button([^>]*)>(.*?)</button>", repl, html, flags=re.DOTALL)


def inject_head(html: str) -> str:
    if "assets/animations.css" in html:
        return html
    return html.replace("</head>", HEAD_INJECT, 1)


def add_reveals(html: str) -> str:
    # Tag <section> elements with data-reveal once
    def section_repl(m: re.Match) -> str:
        attrs = m.group(1)
        if "data-reveal" in attrs:
            return m.group(0)
        return f"<section{attrs} data-reveal>"

    html = re.sub(r"<section([^>]*)>", section_repl, html)

    # Tag inner h1/h2 with data-reveal for staggered entrance
    def head_repl(m: re.Match) -> str:
        tag, attrs = m.group(1), m.group(2)
        if "data-reveal" in attrs:
            return m.group(0)
        return f"<{tag}{attrs} data-reveal data-reveal-delay=\"1\">"

    html = re.sub(r"<(h1|h2)([^>]*)>", head_repl, html)
    return html


def add_motion_classes(html: str) -> str:
    # add hero-parallax on hero image
    html = re.sub(
        r'(<img[^>]*alt="Salon Interior"[^>]*class=")([^"]*)(")',
        r"\1\2 hero-parallax\3",
        html,
    )
    # add brand-float on first brand title in header
    html = re.sub(
        r'(<a[^>]*class="font-headline-lg[^"]*?)("[^>]*>\s*МАРИНА БЬЮТИ)',
        r"\1 brand-float\2",
        html,
        count=1,
    )
    # add kinetic + lift to service / gallery cards (rounded-lg group cards)
    html = re.sub(
        r'(<div class="group[^"]*?)(")',
        r"\1 kinetic lift\2",
        html,
    )
    return html


def main() -> None:
    for name in FILES:
        p = ROOT / name
        s = p.read_text(encoding="utf-8")
        s = A_RE.sub(patch_anchor, s)
        s = rewire_booking_buttons(s)
        s = add_motion_classes(s)
        s = add_reveals(s)
        s = inject_head(s)
        p.write_text(s, encoding="utf-8")
        print(f"patched {name}")


if __name__ == "__main__":
    main()
