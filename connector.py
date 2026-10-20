import json
from datetime import datetime, timedelta

from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Logging as log
from fivetran_connector_sdk import Operations as op
from google_play_scraper import Sort, reviews

TABLE = "google_play_reviews"
LOOKBACK_DAYS = 14   # re-read recent reviews to catch late developer replies
PAGE_SIZE = 200


def schema(configuration: dict):
    # Declare the table and its primary key. Fivetran infers the other columns.
    return [{"table": TABLE, "primary_key": ["review_id"]}]


def to_row(r: dict, app_id: str) -> dict:
    # Map library field names to our column names.
    # userName and userImage are deliberately NOT copied (privacy rule).
    return {
        "review_id": r["reviewId"],
        "app_id": app_id,
        "rating": r["score"],
        "review_text": r["content"],
        "thumbs_up": r["thumbsUpCount"],
        "app_version": r.get("appVersion"),
        "reviewed_at": r["at"].isoformat(),
        "reply_text": r.get("replyContent"),
        "replied_at": r["repliedAt"].isoformat() if r.get("repliedAt") else None,
    }


def sync_app(app_id: str, state: dict, initial_days: int):
    key = f"gplay_{app_id}"
    if key in state:
        cutoff = datetime.fromisoformat(state[key]) - timedelta(days=LOOKBACK_DAYS)
    else:
        cutoff = datetime.now() - timedelta(days=initial_days)

    newest = datetime.fromisoformat(state[key]) if key in state else None
    token, count, done = None, 0, False

    while not done:
        batch, token = reviews(
            app_id, lang="en", country="us", sort=Sort.NEWEST,
            count=PAGE_SIZE, continuation_token=token,
        )
        if not batch:
            break
        for r in batch:
            if r["at"] < cutoff:
                done = True
                break
            op.upsert(table=TABLE, data=to_row(r, app_id))
            count += 1
            if newest is None or r["at"] > newest:
                newest = r["at"]

    if count == 0:
        log.warning(f"{app_id}: 0 reviews returned, check the source")
    log.info(f"{app_id}: upserted {count} reviews, newest {newest}")

    if newest:
        state[key] = newest.isoformat()
    op.checkpoint(state=state)


def update(configuration: dict, state: dict):
    app_ids = [a.strip() for a in configuration["app_ids"].split(",")]
    initial_days = int(configuration.get("initial_days", "30"))
    for app_id in app_ids:
        sync_app(app_id, state, initial_days)


connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    with open("configuration.json") as f:
        connector.debug(configuration=json.load(f))
