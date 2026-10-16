#!/usr/bin/env python3
"""Builds the site from releases.json.

Usage:  python3 tools/build.py
Output: index.html (hub) + one folder per release (<slug>/index.html, cover.jpg, og.jpg, icon.png).

Add a release: append an entry to releases.json, drop its cover in covers/, run this script, commit, push.
"""
import json, os, shutil, subprocess, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

data = json.load(open("releases.json", encoding="utf-8"))
site = data["site"]
releases = sorted(data["releases"], key=lambda r: r["date"], reverse=True)

ICONS = {
    "spotify": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>',
    "applemusic": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M23.994 6.124a9.23 9.23 0 0 0-.24-2.19c-.317-1.31-1.062-2.31-2.18-3.043a5.022 5.022 0 0 0-1.877-.726 10.496 10.496 0 0 0-1.564-.15c-.04-.003-.083-.01-.124-.013H5.986c-.152.01-.303.017-.455.026-.747.043-1.49.123-2.193.4-1.336.53-2.3 1.452-2.865 2.78-.192.448-.292.925-.363 1.408-.056.392-.088.785-.1 1.18 0 .032-.007.062-.01.093v12.223c.01.14.017.283.027.424.05.815.154 1.624.497 2.373.65 1.42 1.738 2.353 3.234 2.801.42.127.856.187 1.293.228.555.053 1.11.06 1.667.06h11.03a12.5 12.5 0 0 0 1.57-.1c.822-.106 1.596-.35 2.295-.81a5.046 5.046 0 0 0 1.88-2.207c.186-.42.293-.87.37-1.324.113-.675.138-1.358.137-2.04-.002-3.8 0-7.595-.003-11.393zm-6.423 3.99v5.712c0 .417-.058.827-.244 1.206-.29.59-.76.962-1.388 1.14-.35.1-.706.157-1.07.173-.95.045-1.773-.6-1.943-1.536a1.88 1.88 0 0 1 1.038-2.022c.323-.16.67-.25 1.018-.324.378-.082.758-.153 1.134-.24.274-.063.457-.23.51-.516a.904.904 0 0 0 .02-.193c0-1.815 0-3.63-.002-5.443a.725.725 0 0 0-.026-.185c-.04-.15-.15-.243-.304-.234-.16.01-.318.035-.475.066-.76.15-1.52.303-2.28.456l-2.325.47-1.374.278c-.016.003-.032.01-.048.013-.277.077-.377.203-.39.49-.002.042 0 .086 0 .13-.002 2.602 0 5.204-.003 7.805 0 .42-.047.836-.215 1.227-.278.64-.77 1.04-1.434 1.233-.35.1-.71.16-1.075.172-.96.036-1.755-.6-1.92-1.544-.14-.812.23-1.685 1.154-2.075.357-.15.73-.232 1.108-.31.287-.06.575-.116.86-.177.383-.083.583-.323.6-.714v-.15c0-2.96 0-5.922.002-8.882 0-.123.013-.25.042-.37.07-.285.273-.448.546-.518.255-.066.515-.112.774-.165.733-.15 1.466-.296 2.2-.444l2.27-.46c.67-.134 1.34-.27 2.01-.403.22-.043.443-.088.664-.106.31-.025.523.17.554.482.008.073.012.148.012.223.002 1.91.002 3.822 0 5.732z"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z"/></svg>',
}
LABELS = {"spotify": "Spotify", "applemusic": "Apple Music", "youtube": "YouTube", "amazon": "Amazon Music", "deezer": "Deezer", "tidal": "TIDAL", "soundcloud": "SoundCloud"}
ORDER = ["spotify", "applemusic", "youtube", "amazon", "deezer", "tidal", "soundcloud"]


def render(tpl, ctx):
    for k, v in ctx.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    missing = [p for p in tpl.split("{{")[1:] if "}}" in p]
    if missing:
        sys.exit("unfilled placeholders: " + ", ".join(m.split("}}")[0] for m in missing))
    return tpl


def buttons(links):
    out = []
    for key in ORDER:
        if key in links:
            icon = ICONS.get(key, '<span class="play">▶</span>')
            out.append(f'      <a class="btn {key}" data-platform="{key}" href="{html.escape(links[key])}">{icon}<span>{LABELS[key]}</span></a>')
    if "more" in links:
        label = links.get("more_label", "Tutte le piattaforme")
        out.append(f'      <a class="btn more" data-platform="more" href="{html.escape(links["more"])}"><span class="play">▶</span><span>{html.escape(label)}</span></a>')
    return "\n".join(out)


def make_images(cover, outdir):
    """cover.jpg (1200), og.jpg (1200), icon.png (192) from the source cover."""
    shutil.copy(cover, os.path.join(outdir, "cover.jpg"))
    subprocess.run(["sips", "-Z", "1200", os.path.join(outdir, "cover.jpg")], check=True, capture_output=True)
    shutil.copy(os.path.join(outdir, "cover.jpg"), os.path.join(outdir, "og.jpg"))
    shutil.copy(os.path.join(outdir, "cover.jpg"), os.path.join(outdir, "icon.png"))
    subprocess.run(["sips", "-s", "format", "png", "-Z", "192", os.path.join(outdir, "icon.png")], check=True, capture_output=True)


artist_title = site["artist"].title()
common = {
    "PIXEL_ID": site["meta_pixel_id"], "ARTIST": site["artist"], "ARTIST_TITLE": artist_title,
    "ARTIST_TAG": site.get("artist_tag", ""), "INSTAGRAM": site["instagram"], "YEAR": site["year"],
    "BASE_URL": site["base_url"].rstrip("/"),
}

release_tpl = open("tools/release.html", encoding="utf-8").read()
cards = []
for r in releases:
    outdir = r["slug"]
    os.makedirs(outdir, exist_ok=True)
    make_images(r["cover"], outdir)
    ctx = dict(common, TITLE=r["title"], TAGLINE=r.get("tagline", ""), URL=f'{common["BASE_URL"]}/{r["slug"]}/',
               BUTTONS=buttons(r["links"]))
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(render(release_tpl, ctx))
    cards.append(
        f'      <a class="card" href="{r["slug"]}/">'
        f'<img src="{r["slug"]}/icon.png" width="96" height="96" alt="">'
        f'<div><div class="t">{html.escape(r["title"])}</div><div class="s"><b>{r["date"][:4]}</b> · {html.escape(r.get("tagline", ""))}</div></div>'
        f'<span class="arrow">▶</span></a>')
    print(f"  {r['slug']}/  ←  {r['title']}")

hub_tpl = open("tools/hub.html", encoding="utf-8").read()
open("index.html", "w", encoding="utf-8").write(render(hub_tpl, dict(common, LATEST_SLUG=releases[0]["slug"], CARDS="\n".join(cards))))
open(".nojekyll", "w").close()
print(f"  index.html  ←  hub ({len(releases)} release)")
