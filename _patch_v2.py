"""Patch v2: targeted motion enrichment per page.
- index.html: stagger service cards, hero blob, hero CTA pulse
- gallery.html: stagger items + kenburns + chip-fx
- price.html:  stagger 3 categories + price-row + kenburns on top images + lift
- booking.html: stagger inner service cards + lift, step-num class
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).parent


def add_class(html: str, marker: str, extra: str) -> str:
    """Append `extra` classes to the FIRST element that contains `marker` substring.
    `marker` is a substring of the opening tag attribute set."""
    pat = re.compile(r'(<[a-zA-Z]+[^>]*?class=")([^"]*?)("[^>]*?' + re.escape(marker) + r'[^>]*?>)')
    return pat.sub(lambda m: f"{m.group(1)}{m.group(2)} {extra}{m.group(3)}", html, count=1)


def stagger_children(html: str, container_marker: str, child_open: str, max_delay: int = 5) -> str:
    """Within first element matched by container_marker, add data-reveal + delay to children matching child_open."""
    # Locate opening tag of container
    idx = html.find(container_marker)
    if idx == -1:
        return html
    # Find end of opening tag '>'
    start = html.find(">", idx) + 1
    # Find matching closing '</div>' naively at same depth. Use a depth scanner.
    depth = 1
    i = start
    tag_open = re.compile(r"<([a-zA-Z]+)[^>]*?>")
    tag_close = re.compile(r"</([a-zA-Z]+)>")
    # Determine container tag name from container_marker piece
    # Container marker like 'class="grid grid-cols-1 md:grid-cols-3 gap-8"' — we need the tag preceding it
    container_tag_match = re.search(r"<([a-zA-Z]+)[^<>]*" + re.escape(container_marker.split('"')[0]), html[max(0, idx-200):idx+len(container_marker)])
    container_tag = container_tag_match.group(1) if container_tag_match else "div"

    # Walk
    end = -1
    cursor = start
    while cursor < len(html) and depth > 0:
        mo = tag_open.search(html, cursor)
        mc = tag_close.search(html, cursor)
        if not mc:
            break
        if mo and mo.start() < mc.start():
            if mo.group(1) == container_tag:
                depth += 1
            cursor = mo.end()
        else:
            if mc.group(1) == container_tag:
                depth -= 1
                if depth == 0:
                    end = mc.start()
                    break
            cursor = mc.end()
    if end == -1:
        return html

    inner = html[start:end]
    counter = {"n": 0}

    def repl(m: re.Match) -> str:
        counter["n"] += 1
        d = min(counter["n"], max_delay)
        attrs = m.group(1)
        if "data-reveal" in attrs:
            return m.group(0)
        return f"<{child_open}{attrs} data-reveal data-reveal-delay=\"{d}\" lift kinetic-marker"

    # Replace direct children with given child_open
    inner_new = re.sub(
        rf"<{re.escape(child_open)}([^>]*)",
        repl,
        inner,
    )
    # Add class kinetic + lift via a follow-up pass on the marked tokens
    inner_new = re.sub(
        r'(<' + re.escape(child_open) + r'[^>]*?class=")([^"]*?)("[^>]*?)\s+lift kinetic-marker',
        r'\1\2 kinetic lift\3',
        inner_new,
    )
    return html[:start] + inner_new + html[end:]


def patch_index() -> None:
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")

    # Inject decorative blob in hero section right after section opening
    s = s.replace(
        '<section class="relative w-full min-h-[819px] flex items-center bg-surface-variant overflow-hidden" data-reveal>',
        '<section class="relative w-full min-h-[819px] flex items-center bg-surface-variant overflow-hidden" data-reveal>\n'
        '<div class="blob bg-primary-fixed-dim" style="width:520px;height:520px;top:-160px;right:-180px;"></div>\n'
        '<div class="blob bg-tertiary-fixed-dim" style="width:380px;height:380px;bottom:-140px;left:-120px;animation-delay:-4s;"></div>',
        1,
    )

    # Add h-underline accent on "Наши Услуги"
    s = s.replace(
        '<h2 class="font-headline-lg text-headline-lg text-on-surface mb-4" data-reveal data-reveal-delay="1">Наши Услуги</h2>',
        '<h2 class="font-headline-lg text-headline-lg text-on-surface mb-4 inline-block" data-reveal data-reveal-delay="1"><span class="h-underline">Наши Услуги</span></h2>',
        1,
    )
    s = s.replace(
        '<div class="w-16 h-1 bg-primary mx-auto rounded-full"></div>',
        '',
        1,
    )

    # Stagger 3 service cards: they share class 'group relative bg-surface-container-lowest'
    s = stagger_children(
        s,
        container_marker='class="grid grid-cols-1 md:grid-cols-3 gap-8"',
        child_open="div",
    )

    p.write_text(s, encoding="utf-8")
    print("patched index.html (v2)")


def patch_gallery() -> None:
    p = ROOT / "gallery.html"
    s = p.read_text(encoding="utf-8")

    # h-underline on H1
    s = s.replace(
        '<h1 class="font-headline-xl text-headline-xl md:font-headline-xl md:text-headline-xl text-on-surface mb-4" data-reveal data-reveal-delay="1">Наши работы</h1>',
        '<h1 class="font-headline-xl text-headline-xl md:font-headline-xl md:text-headline-xl text-on-surface mb-4 inline-block" data-reveal data-reveal-delay="1"><span class="h-underline">Наши работы</span></h1>',
        1,
    )

    # Add chip-fx to filter buttons
    s = re.sub(
        r'(<button class="bg-primary/10 text-primary px-6 py-3 rounded-full font-label-sm text-label-sm hover:bg-primary/20 transition-colors border border-primary/20)',
        r'\1 chip-fx',
        s,
    )
    s = re.sub(
        r'(<button class="bg-surface text-on-surface-variant px-6 py-3 rounded-full font-label-sm text-label-sm hover:bg-surface-variant transition-colors border border-outline-variant)',
        r'\1 chip-fx',
        s,
    )

    # Stagger gallery items + kenburns/lift
    s = stagger_children(
        s,
        container_marker='class="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[300px]"',
        child_open="div",
    )
    # Add `kenburns` to the same items (look for the rounded-xl overflow-hidden relative group pattern)
    s = re.sub(
        r'(<div[^>]*class="[^"]*rounded-xl overflow-hidden relative group[^"]*?)(")',
        r"\1 kenburns\2",
        s,
    )

    p.write_text(s, encoding="utf-8")
    print("patched gallery.html (v2)")


def patch_price() -> None:
    p = ROOT / "price.html"
    s = p.read_text(encoding="utf-8")

    # h-underline on H1
    s = s.replace(
        '<h1 class="font-headline-xl-mobile md:font-headline-xl text-headline-xl-mobile md:text-headline-xl text-primary mb-4" data-reveal data-reveal-delay="1">Прайс-лист</h1>',
        '<h1 class="font-headline-xl-mobile md:font-headline-xl text-headline-xl-mobile md:text-headline-xl text-primary mb-4 inline-block" data-reveal data-reveal-delay="1"><span class="h-underline">Прайс-лист</span></h1>',
        1,
    )

    # Add price-row to <li> rows
    s = re.sub(
        r'(<li class="flex justify-between items-center border-b border-outline-variant/20 pb-3 hover:text-primary transition-colors group cursor-default)',
        r'\1 price-row',
        s,
    )

    # Stagger 3 category cards
    s = stagger_children(
        s,
        container_marker='class="grid grid-cols-1 lg:grid-cols-3 gap-8"',
        child_open="div",
    )

    # CTA banner reveal
    s = s.replace(
        '<div class="mt-24 bg-surface-container rounded-xl p-10 flex flex-col md:flex-row items-center justify-between shadow-sm border border-outline-variant/20">',
        '<div class="mt-24 bg-surface-container rounded-xl p-10 flex flex-col md:flex-row items-center justify-between shadow-sm border border-outline-variant/20" data-reveal data-reveal="scale">',
        1,
    )

    p.write_text(s, encoding="utf-8")
    print("patched price.html (v2)")


def patch_booking() -> None:
    p = ROOT / "booking.html"
    s = p.read_text(encoding="utf-8")

    # h-underline on H1 (desktop one)
    s = s.replace(
        '<h1 class="font-headline-xl text-headline-xl text-primary mb-4 hidden md:block" data-reveal data-reveal-delay="1">Онлайн Запись</h1>',
        '<h1 class="font-headline-xl text-headline-xl text-primary mb-4 hidden md:block inline-block" data-reveal data-reveal-delay="1"><span class="h-underline">Онлайн Запись</span></h1>',
        1,
    )

    # step-num class on the small numbered circles
    s = re.sub(
        r'(<div class="w-8 h-8 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-label-sm text-label-sm mr-4")',
        r'<div class="w-8 h-8 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-label-sm text-label-sm mr-4 step-num"',
        s,
    )
    s = re.sub(
        r'(<div class="w-8 h-8 rounded-full border-2 border-outline-variant text-outline-variant flex items-center justify-center font-label-sm text-label-sm mr-4")',
        r'<div class="w-8 h-8 rounded-full border-2 border-outline-variant text-outline-variant flex items-center justify-center font-label-sm text-label-sm mr-4 step-num"',
        s,
    )

    # Stagger inner service cards
    s = stagger_children(
        s,
        container_marker='class="grid grid-cols-1 md:grid-cols-2 gap-4"',
        child_open="div",
    )

    # Sticky summary on right column reveal from right
    s = s.replace(
        '<div class="sticky top-32 bg-surface-container rounded-xl p-8 border border-outline-variant shadow-sm">',
        '<div class="sticky top-32 bg-surface-container rounded-xl p-8 border border-outline-variant shadow-sm" data-reveal="right">',
        1,
    )

    p.write_text(s, encoding="utf-8")
    print("patched booking.html (v2)")


def main() -> None:
    patch_index()
    patch_gallery()
    patch_price()
    patch_booking()


if __name__ == "__main__":
    main()
