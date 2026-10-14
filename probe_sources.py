"""
Day 1 probe: can this machine pull meditation app reviews from
Google Play and the Apple App Store?

Run:  python probe_sources.py
Output: data/sample/gplay_sample.csv and data/sample/appstore_sample.csv
Reviewer names are dropped on purpose (no personal data downstream).
"""

import csv
import os
import sys

import requests
from google_play_scraper import Sort, reviews

# Headspace on both stores. Swap in other apps later.
GPLAY_APP_ID = "com.getsomeheadspace.android"   # from play.google.com/store/apps/details?id=...
APPLE_APP_ID = "493145008"                      # from apps.apple.com/us/app/.../id<NUMBER>

OUT_DIR = os.path.join("data", "sample")
os.makedirs(OUT_DIR, exist_ok=True)


def probe_google_play(n=200):
    print(f"\n[Google Play] fetching {n} newest reviews for {GPLAY_APP_ID} ...")
    try:
        result, token = reviews(
            GPLAY_APP_ID, lang="en", country="us", sort=Sort.NEWEST, count=n
        )
    except Exception as e:
        print(f"[Google Play] FAILED: {type(e).__name__}: {e}")
        return False

    rows = [
        {
            "review_id": r.get("reviewId"),
            "rating": r.get("score"),
            "review_text": r.get("content"),
            "thumbs_up": r.get("thumbsUpCount"),
            "app_version": r.get("appVersion"),
            "reviewed_at": r.get("at"),
            "dev_reply": r.get("replyContent"),
            "dev_replied_at": r.get("repliedAt"),
        }
        for r in result
    ]
    path = os.path.join(OUT_DIR, "gplay_sample.csv")
    write_csv(path, rows)
    with_version = sum(1 for r in rows if r["app_version"])
    with_reply = sum(1 for r in rows if r["dev_reply"])
    print(f"[Google Play] OK: {len(rows)} reviews -> {path}")
    print(f"              {with_version} have app_version, {with_reply} have a developer reply")
    print(f"              continuation token present: {token is not None}")
    return True


def probe_app_store(pages=1):
    print(f"\n[App Store] fetching {pages} page(s) for id {APPLE_APP_ID} ...")
    rows = []
    for page in range(1, pages + 1):
        url = (
            "https://itunes.apple.com/rss/customerreviews/"
            f"page={page}/id={APPLE_APP_ID}/sortby=mostrecent/json?cc=us"
        )
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            entries = resp.json().get("feed", {}).get("entry", [])
        except Exception as e:
            print(f"[App Store] FAILED on page {page}: {type(e).__name__}: {e}")
            return False

        if isinstance(entries, dict):  # a single entry comes back as a dict
            entries = [entries]
        for e in entries:
            if "im:rating" not in e:   # skip non-review entries
                continue
            rows.append(
                {
                    "review_id": e["id"]["label"],
                    "rating": e["im:rating"]["label"],
                    "title": e["title"]["label"],
                    "review_text": e["content"]["label"],
                    "app_version": e.get("im:version", {}).get("label"),
                    "reviewed_at": e.get("updated", {}).get("label"),
                }
            )

    if not rows:
        print("[App Store] Feed answered but returned 0 reviews (feed may be limited in this region).")
        return False
    path = os.path.join(OUT_DIR, "appstore_sample.csv")
    write_csv(path, rows)
    print(f"[App Store] OK: {len(rows)} reviews -> {path}")
    return True


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    gp = probe_google_play()
    ap = probe_app_store()
    print("\nSUMMARY  Google Play:", "PASS" if gp else "FAIL", "| App Store:", "PASS" if ap else "FAIL")
    sys.exit(0 if (gp and ap) else 1)
