# AEVEL HQ - GEMINI.MD (Project Constitution)

## 1. Core Principles
- **Reliability > Speed**: Correctness and auditability are paramount.
- **Data-First**: All IO must have defined schemas here. Validated before execution.
- **Access Control**: Internal only. No external sharing.
- **Deterministic**: No guessing. Verify against Source of Truth.
- **Audit**: Log every action in `progress.md` and `audit_log.jsonl`.

## 2. B.L.A.S.T. Configuration (Phase 1)

### North Star
**Automate the Daily Executive Brief** consolidating:
- Notion (Meeting notes, Projects)
- Gmail (Flagged items)
- Google Sheets/Analytics (Metrics)
- Internal Task Tracker

### Source of Truth (SoT)
| Domain | Source System |
| :--- | :--- |
| **Tasks & Projects** | Notion (Primary) |
| **Meeting Notes** | Notion (Primary), Slack (Secondary) |
| **Analytics** | Google Sheets + Internal CSVs |
| **Emails** | Gmail (Flagged) |
| **Schedule** | Google Calendar |

### Integrations
- **Notion API** (Tasks, Pages)
- **Gmail API** (Read-only for flagged)
- **Google Calendar API** (Read-only for schedule)
- **Google Sheets API** (Read-only for metrics)
- **Slack Webhooks** (Notifications)

### Delivery Payloads
1. **Aevel HQ Dashboard** (Internal Web UI)
2. **Slack Daily Brief** (Block Kit)
3. **Google Docs/Sheets** (Executive Report)
4. **Email Digest** (HTML)

## 3. Global Schemas

### 3.1. Executive Brief Data Model
The central object aggregating daily info.
```json
{
  "date": "YYYY-MM-DD",
  "generated_at": "ISO8601",
  "priorities": ["Task Object", "Task Object"],
  "metrics": [
    {
      "name": "Daily Active Users",
      "value": 1234,
      "change": "+5%",
      "source": "Google Sheets"
    }
  ],
  "meeting_summaries": [
    {
      "title": "Product Sync",
      "decisions": ["...", "..."],
      "action_items": ["..."]
    }
  ],
  "flagged_emails": [
    {
      "subject": "Urgent: Client X",
      "summary": "...",
      "link": "https://mail.google.com/..."
    }
  ]
}
```

### 3.2. Task Object (Normalized)
Unifies Notion and Internal tasks.
```json
{
  "id": "uuid-or-source-id",
  "title": "Task Name",
  "status": "Todo" | "In Progress" | "Done",
  "priority": "High" | "Medium" | "Low",
  "owner": "Name",
  "due_date": "YYYY-MM-DD",
  "source": "Notion",
  "source_url": "https://notion.so/..."
}
```

### 3.3. Metric Object
```json
{
  "key": "unique_metric_key",
  "label": "Human Readable Label",
  "value": 100.5,
  "unit": "USD" | "Count" | "Percent",
  "period": "Daily" | "Weekly",
  "source_system": "Google Sheets"
}
```

### 3.4. Meeting Intelligence Schema
Object representing deep analysis of a meeting.
```json
{
  "meeting_id": "uuid",
  "title": "Strategy Sync",
  "date": "YYYY-MM-DD",
  "attendees": ["Person A", "Person B"],
  "analysis": {
    "summary": "High-level summary...",
    "decisions": ["Decision 1", "Decision 2"],
    "action_items": [
      {"task": "Do X", "owner": "Person A", "status": "Open"}
    ],
    "keywords": ["Campaign", "Budget"]
  }
}
```

### 3.5. Calendar Intelligence Schema
Object representing schedule analysis.
```json
{
  "events": [
    {
      "event_id": "string",
      "summary": "Meeting with Client",
      "start": "ISO8601",
      "end": "ISO8601",
      "attendees": ["email@example.com"],
      "link": "https://meet.google.com/..."
    }
  ],
  "analysis": {
    "conflicts": [
      {"event_a": "ID1", "event_b": "ID2", "reason": "Overlapping time"}
    ],
    "high_priority": ["ID1"],
    "free_blocks": [{"start": "ISO", "end": "ISO"}],
    "related_meetings": [{"event_id": "ID1", "notion_meeting_id": "UUID"}]
  }
}
```

### 3.6. Work Order Schema (Module 4)
Object representing the prioritized list of work.
```json
{
  "work_order_id": "uuid",
  "date": "YYYY-MM-DD",
  "total_open_tasks": 15,
  "top_score": 95,
  "tasks": [
    {
      "task_id": "uuid",
      "title": "Complete Proposal",
      "priority": "High",
      "due_date": "YYYY-MM-DD",
      "score": 95,
      "tag": "Must Do"
    }
  ]
}
```

## 4. Maintenance Log
- [2026-02-01] Discovery Phase complete. Schemas defined.
- [2026-02-01] Initial creation.
