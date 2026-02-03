# SOP: Task & Operations Manager (Module 04)

## 1. Objective
Transform a flat list of tasks into a prioritized "Work Order" by calculating execution scores based on Due Date, Priority, and Status.

## 2. Inputs
- **Source**: Notion "Tasks" (or "Milestones") Database.
- **Properties Used**:
    - `Name` (Title)
    - `Status` (To Do, In Progress, etc.)
    - `Due Date` (if available)
    - `Priority` (High, Medium, Low - if available)

## 3. Processing Logic
1.  **Fetch**: Retrieve all non-archived, non-Done tasks.
2.  **Filter**: Exclude items with "Someday" status or strictly future start dates (if applicable).
3.  **Score (Ranking Algorithm)**:
    - **Base Score**: 50
    - **Priority Modifier**: High (+30), Medium (+10), Low (-10).
    - **Urgency Modifier**:
        - Overdue: +40
        - Due Today: +20
        - Due Tomorrow: +10
    - **Status Modifier**: In Progress (+15).
4.  **Sort**: Descending order by `score`.
5.  **Output**: Top 3-5 tasks designated as "Daily Objectives".

## 4. Output Schema
See `gemini.md` -> `3.6. Work Order Schema`.

## 5. Triggers
- Runs as part of `tools/navigation.py`.
