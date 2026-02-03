# SOP: Daily Executive Brief (Module 01)

## 1. Objective
Generate a consolidated morning brief for executives, summarizing meetings, tasks, risks, and KPIs.

## 2. Inputs & Sources
- **Calendar**: Retrieve events for T-1 (yesterday) and T0 (today).
- **Notion**:
    - Query `Meeting Notes` DB for entries modified in last 24h.
    - Query `Tasks` DB for "High Priority" items not "Done".
- **Gmail**: Query messages with label `Executive Alert` or `Flagged`.
- **Analytics**: Fetch `Daily Active Users` and `Revenue` from Google Sheets.

## 3. Processing Logic (The "Brain")
1. **Aggregation**: Collect raw data from all sources into `staging_brief.json`.
2. **Filtering**:
    - Discard meetings with no notes/outcomes.
    - Limit tasks to top 5 by urgency.
    - Summarize email threads to <50 words.
3. **Synthesis**:
    - Generate "Day at a Glance" summary.
    - Highlight "Decisions Needed".
4. **Formatting**:
    - Create Slack Block Kit payload.
    - Create HTML email body.

## 4. Output Schema (Target)
See `gemini.md` -> `3.1. Executive Brief Data Model`.

## 5. Execution Triggers
- **Schedule**: Daily at 08:00 AM Local.
- **Manual**: Via Slack command `/aevel-brief`.

## 6. Access Control
- **Recipients**: Executive Channel (Slack), Executive List (Email).
- **Data Sensitivity**: HIGH. Do not log PII or sensitive financials in plaintext debug logs in non-secure envs.
