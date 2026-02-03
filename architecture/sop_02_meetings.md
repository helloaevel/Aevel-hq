# SOP: Meeting Intelligence Engine (Module 02)

## 1. Objective
Extract structured insights (Decisions, Action Items) from unstructured Notion meeting notes to ensure follow-through.

## 2. Inputs
- **Source**: Notion "Meeting Notes" Database (ID: `NOTION_MEETING_DB_ID`).
- **Data**: Page Properties (Date, Attendees) + Page Content (Blocks).

## 3. Processing Logic
1.  **Fetch**: Identify meetings from "Yesterday" or "Today" that are marked `Done` or have content.
2.  **Parse**:
    - Retrieve children blocks of the page.
    - Look for:
        - Bullet points following "Decisions" header.
        - Checkboxes (To-Do blocks) for Action Items.
    - *Future AI*: Pass transcript/text to LLM for summarization.
3.  **Analyze**:
    - Count open vs. closed items.
    - Identify key stakeholders (Attendees).
4.  **Output**:
    - structured JSON (`meeting_analysis.json`).
    - Append to `Daily Executive Brief` if relevant.

## 4. Output Schema
See `gemini.md` -> `3.4. Meeting Intelligence Schema`.

## 5. Triggers
- Runs as part of `run_daily_brief.bat` (eventually).
- Standalone via `python tools/analyze_meetings.py`.
