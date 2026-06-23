# Autoresearch Ads Experts

This directory contains Cosmos expert bundles for the Autoresearch Ads workflow.

## Architecture

Use two experts, not one:

1. **Autoresearch Ads Reporter**
   - Scheduled daily.
   - Pulls Google Ads data, refreshes `data/snapshot.json`, reconciles campaigns,
     analyzes performance, and posts a concise Slack summary with proposed experiments.
   - Does **not** mutate Google Ads.
   - Writes a pending approval record to org VFS.

2. **Autoresearch Ads Approval Handler**
   - Triggered by Slack replies in the report thread.
   - Parses commands such as `approve all`, `approve 1,3`, `reject all`, and `status`.
   - Loads the pending approval record from org VFS.
   - After approval, validates and executes Google Ads changes, then logs results.

## Why separate experts?

Scheduled reporting and Slack approval are different event lifecycles:

- The reporter should run once, post, then stop.
- Approval can happen minutes or hours later from a Slack message event.
- A separate handler keeps the scheduled run from staying alive just to wait.
- It also narrows mutation rights: only the handler is allowed to deploy approved changes.

## Shared state

Both experts use organization VFS as cross-session state:

- `autoresearch-ads/pending-approvals.jsonl` — append-only pending/handled proposal records
- `autoresearch-ads/deployment-log.jsonl` — append-only deployment outcomes

Each pending record is keyed by Slack `channel_id` + root `thread_ts`, so a reply in
the thread resolves to exactly one proposal bundle.

## Apply order

Validate both bundles first:

- `auggie cloud expert validate -f experts/autoresearch-ads-reporter.yaml`
- `auggie cloud expert validate -f experts/autoresearch-ads-approval-handler.yaml`

Apply only after review/approval:

- `auggie cloud expert apply -f experts/autoresearch-ads-reporter.yaml`
- `auggie cloud expert apply -f experts/autoresearch-ads-approval-handler.yaml`

## Scope note

These bundles are `visibility: user` because the attached Google Ads MCP config is
currently user-scoped. To make them tenant/shared experts, promote the Google Ads
MCP registry entry to tenant scope first, then update `visibility` accordingly.