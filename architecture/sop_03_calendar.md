# SOP: Calendar & Scheduling Brain (Module 03)

## 1. Objective
Proactively manage the user's time by identifying upcoming commitments, detecting conflicts, and linking calendar events to prepared meeting notes.

## 2. Inputs
- **Primary Source**: Google Calendar (via OAuth 2.0).
- **Secondary Source**: Notion "Meeting Notes" (for cross-referencing).
- **Scope**: "Today" + Next 24 Hours.

## 3. Processing Logic
1.  **Fetch**:
    - Retrieve events from Google Calendar for the target window.
    - Filter out "Declined" events.
2.  **Analyze**:
    - **Conflict Detection**: Identify overlapping time ranges.
    - **Priority Tagging**: events with key keywords ("Strategy", "Client", "Board") are marked High Priority.
    - **Cross-Reference**:
        - Search Notion Meeting Notes for pages matching the Event Title.
        - If found, link the ID. If not, flag as "No Note Prepared".
3.  **Output**:
    - `schedule_analysis.json` containing the raw events and the computed analysis.

## 4. Output Schema
See `gemini.md` -> `3.5. Calendar Intelligence Schema`.

## 5. Triggers
- Runs as part of `tools/navigation.py`.
- Executed daily at 08:00 AM (via `run_daily_brief.bat`).
