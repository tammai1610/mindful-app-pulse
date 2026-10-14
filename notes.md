# Probe notes
- Google Play: 200 Headspace reviews, 163 have app_version (81%), 6 have a dev reply (3%)
- App Store: 50 reviews per page; working URL uses ?cc=us and lowercase sortby=mostrecent
- Old /us/rss/ URL returns 200 OK but no reviews

# Connector design
1. Tables
The connector delivers tables in Snowflake:
- google_play_reviews
- app_store_reviews
2. Primary Keys
- review_id for both. Every review has it s own ID  from the store, and it never changes.
3. Bookmark (What would you save so the next run knows where to start)
- State:
`{"gplay_newest_review_at": "2026-10-14T09:12:00",
 "appstore_newest_review_at": "2026-10-14T08:40:00"}
- On the next run, the connector reads the state and only fetches reviews newer than that time.
- Tests (like dbt’s unique test on review_id) detect duplicates after they’ve landed. They’re a smoke alarm. What prevents duplicates is the primary key plus upsert at load time. When the retried run delivers a review that’s already there, Fivetran sees the same review_id, overwrites the existing row instead of adding a new one, and still ends up with one row. That’s idempotency.