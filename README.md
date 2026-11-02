# Mindful App Pulse

Mindful App Pulse turns public app store reviews for five meditation and mental health apps into answers a product manager can act on: which releases hurt ratings, what users complain about, and how fast developers respond.

Status: in progress (Phase 1 of 6: building the Fivetran connector)

## Problem

A PM at Calm or Headspace can see their star rating move, but not why. Was it the last release, a new paywall, or an unpopular AI feature? This project collects Google Play and App Store reviews for Calm, Headspace, Insight Timer, Medito and Finch through a custom Fivetran connector, then models them in dbt to tie rating changes to app versions and complaint topics. The dataset is built from scratch and grows with every daily sync, because Apple only shows the newest ~500 reviews per app. Medito, a free nonprofit app, acts as a control group for paywall complaints.

## Product questions

1. Release impact: how does the average rating change from version to version?
2. Monetization pain: what share of complaints are about paywalls or pricing, by app?
3. Developer responsiveness: how often and how fast do developers reply (Google Play)?
4. AI features: how do users feel about AI coaching features?
5. Gen Z-leaning vs. classic apps: how does the complaint mix differ (Finch vs. Calm)?

## Stack

Fivetran Connector SDK (custom Python) -> Snowflake -> dbt Core -> Snowflake semantic view -> Cortex Analyst

## Data and privacy

- Google Play: `google-play-scraper` (unofficial; reads public store pages).
- Apple App Store: public customer-reviews RSS feed (newest ~500 reviews per app).
- Reviewer names are dropped at extraction. Raw review text is never committed to this repo.

## Run it yourself

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt

## Results

Coming in Phase 6: a PM-facing insights memo.

## What I'd do next

Coming later.
