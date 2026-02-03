import json
from datetime import datetime

class BriefStylizer:
    @staticmethod
    def to_slack_blocks(data):
        """Converts daily brief data to Slack Block Kit format."""
        date_str = data.get("date", "Today")
        summary = data.get("summary", {})
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Daily Executive Brief 📅 {date_str}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Tasks:* {summary.get('task_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Meetings:* {summary.get('meeting_count', 0)}"},
                    {"type": "mrkdwn", "text": f"*Urgent:* {summary.get('urgent_email_count', 0)}"}
                ]
            },
            {"type": "divider"}
        ]

        # Priorities (Work Order)
        tasks = data.get("priorities", [])
        if tasks:
            task_lines = []
            for t in tasks:
                status_icon = "✅" if t.get("status") == "Done" else "⚠️" if t.get("status") == "In progress" else "⭕"
                
                # Score visualization
                score = t.get("score", 0)
                score_str = f"`{score}`" if score else ""
                
                # Priority icon
                prio = t.get("priority", "Medium")
                prio_icon = "🔥" if prio == "High" else "🔽" if prio == "Low" else "🔹"
                
                line = f"{score_str} {prio_icon} {status_icon} *<{t.get('url', '#')}|{t.get('title', 'Untitled')}>*"
                task_lines.append(line)
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 Work Order (Top 5)*\n" + "\n".join(task_lines)
                }
            })
        else:
             blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🏆 Work Order*\n_No tasks found._"}
            })

        # Schedule (New Calendar Intelligence)
        schedule = data.get("schedule", {})
        events = schedule.get("events", [])
        analysis = schedule.get("analysis", {})
        conflicts = analysis.get("conflicts", [])
        
        if events:
            meet_lines = []
            for m in events:
                # Format time
                dt_obj = datetime.fromisoformat(m["start"].replace('Z', '+00:00'))
                time_str = dt_obj.strftime("%H:%M")
                
                # Tags & Icons
                icon = "📅"
                tags = ""
                if "tags" in m and m["tags"]:
                    tags = f" `{' '.join(m['tags'])}`"
                    if "High Priority" in m["tags"]:
                        icon = "⭐"
                
                line = f"{icon} *{time_str}*: <{m.get('link', '#')}|{m.get('summary', 'Untitled')}> {tags}"
                meet_lines.append(line)
            
            # Conflict Warnings
            if conflicts:
                meet_lines.append("\n*⚠️ Conflicts Detected:*")
                for c in conflicts:
                    meet_lines.append(f"• {c['reason']}")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🗓️ Today's Schedule*\n" + "\n".join(meet_lines)
                }
            })
        else:
             blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🗓️ Today's Schedule*\n_No events found on Google Calendar._"}
            })

        # Meeting Intelligence (Insights)
        insights = data.get("meeting_insights", [])
        has_insights = False
        insight_blocks = []
        
        for i in insights:
            analysis = i.get("analysis", {})
            decisions = analysis.get("decisions", [])
            actions = analysis.get("action_items", [])
            
            if decisions or actions:
                has_insights = True
                title = i.get("title", "Untitled")
                
                text = f"*🧠 {title}*\n"
                if decisions:
                    text += "*Decisions:*\n" + "\n".join([f"• {d}" for d in decisions]) + "\n"
                if actions:
                    text += "*Actions:*\n" + "\n".join([f"• {'☑️' if a['status']=='Done' else '🔲'} {a['task']}" for a in actions])
                
                insight_blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text}
                })

        if has_insights:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "header", 
                "text": {"type": "plain_text", "text": "Meeting Intelligence"}
            })
            blocks.extend(insight_blocks)

        # Alerts (Emails)
        emails = data.get("flagged_emails", [])
        if emails:
            email_lines = []
            for e in emails:
                line = f"🚨 *{e.get('subject', 'No Subject')}*\nFrom: {e.get('sender', 'Unknown')}"
                email_lines.append(line)
                
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📨 Urgent Comms*\n" + "\n\n".join(email_lines)
                }
            })

        # KPIs
        metrics = data.get("metrics", [])
        if metrics:
            metric_lines = []
            for m in metrics:
                line = f"• *{m.get('metric', 'Metric')}*: {m.get('value', '0')}"
                metric_lines.append(line)
                
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 KPIs*\n" + "\n".join(metric_lines)
                }
            })
            
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"Generated at {data.get('generated_at')}"}]
        })

        return {"blocks": blocks}

    @staticmethod
    def to_email_html(data):
        """Converts daily brief data to HTML Email format."""
        date_str = data.get("date", "Today")
        summary = data.get("summary", {})
        
        # Styles
        style = """
        <style>
            body { font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; }
            h1 { font-size: 24px; color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            h2 { font-size: 18px; color: #2980b9; margin-top: 20px; }
            .summary { margin-bottom: 20px; background: #f9f9f9; padding: 15px; border-radius: 5px; }
            .summary span { margin-right: 15px; font-weight: bold; }
            ul { list-style-type: none; padding: 0; }
            li { padding: 8px 0; border-bottom: 1px solid #eee; }
            .urgent { color: #c0392b; font-weight: bold; }
            .footer { font-size: 12px; color: #999; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
            a { color: #3498db; text-decoration: none; }
        </style>
        """
        
        html = [f"<html><head>{style}</head><body>"]
        html.append(f"<h1>Daily Executive Brief 📅 {date_str}</h1>")
        
        # Summary
        html.append(f"""
        <div class="summary">
            <span>Tasks: {summary.get('task_count', 0)}</span>
            <span>Meetings: {summary.get('meeting_count', 0)}</span>
            <span>Urgent: {summary.get('urgent_email_count', 0)}</span>
        </div>
        """)
        
        # Priorities (Work Order)
        html.append("<h2>🏆 Work Order (Top 5)</h2><ul>")
        tasks = data.get("priorities", [])
        if tasks:
            for t in tasks:
                status_icon = "✅" if t.get("status") == "Done" else "⭕"
                prio = t.get("priority", "Medium")
                score = t.get("score", 0)
                
                color = "#000"
                if prio == "High": color = "#d35400"
                
                html.append(f"<li><span style='background:#eee; padding:2px 5px; border-radius:3px; font-family:monospace; margin-right:5px;'>{score}</span> <span style='color:{color}; font-weight:bold;'>{prio}</span> {status_icon} <a href='{t.get('url', '#')}'>{t.get('title', 'Untitled')}</a></li>")
        else:
            html.append("<li><i>No tasks found.</i></li>")
        html.append("</ul>")

        # Schedule (New Calendar Intelligence)
        schedule = data.get("schedule", {})
        events = schedule.get("events", [])
        analysis = schedule.get("analysis", {})
        conflicts = analysis.get("conflicts", [])
        
        html.append("<h2>🗓️ Today's Schedule</h2>")
        
        if conflicts:
            html.append("<div style='background:#ffe6e6; padding:10px; border:1px solid #ffcccc; margin-bottom:10px;'>")
            html.append("<b>⚠️ Conflicts Detected:</b><ul>")
            for c in conflicts:
                html.append(f"<li>{c['reason']}</li>")
            html.append("</ul></div>")

        if events:
            html.append("<ul>")
            for m in events:
                dt_obj = datetime.fromisoformat(m["start"].replace('Z', '+00:00'))
                time_str = dt_obj.strftime("%H:%M")
                
                tags = ""
                style = ""
                if "tags" in m and "High Priority" in m["tags"]:
                     tags = "<span style='background:#fff3cd; padding:2px 5px; border-radius:3px; font-size:0.8em; margin-left:5px;'>⭐ High Priority</span>"
                     style = "font-weight:bold;"
                     
                html.append(f"<li style='{style}'>{time_str}: <a href='{m.get('link', '#')}'>{m.get('summary', 'Untitled')}</a> {tags}</li>")
            html.append("</ul>")
        else:
            html.append("<p><i>No events found on Google Calendar.</i></p>")
        
        # Meeting Intelligence
        insights = data.get("meeting_insights", [])
        has_insights = False
        insight_html = []
        
        for i in insights:
            analysis = i.get("analysis", {})
            decisions = analysis.get("decisions", [])
            actions = analysis.get("action_items", [])
            
            if decisions or actions:
                has_insights = True
                title = i.get("title", "Untitled")
                
                insight_html.append(f"<h3>🧠 {title}</h3>")
                if decisions:
                    insight_html.append("<b>Decisions:</b><ul>")
                    for d in decisions:
                        insight_html.append(f"<li>{d}</li>")
                    insight_html.append("</ul>")
                if actions:
                    insight_html.append("<b>Actions:</b><ul>")
                    for a in actions:
                        status_icon = "☑️" if a['status']=='Done' else "🔲"
                        insight_html.append(f"<li>{status_icon} {a['task']}</li>")
                    insight_html.append("</ul>")

        if has_insights:
            html.append("<h2>Meeting Intelligence</h2>")
            html.extend(insight_html)

        # Alerts
        emails = data.get("flagged_emails", [])
        if emails:
             html.append("<h2>📨 Urgent Comms</h2><ul>")
             for e in emails:
                 html.append(f"<li class='urgent'>🚨 {e.get('subject', 'No Subject')}<br/><small style='color:#666; font-weight:normal;'>From: {e.get('sender', 'Unknown')}</small></li>")
             html.append("</ul>")
             
        # KPIs
        metrics = data.get("metrics", [])
        if metrics:
            html.append("<h2>📈 KPIs</h2><ul>")
            for m in metrics:
                html.append(f"<li><b>{m.get('metric', 'Metric')}</b>: {m.get('value', '0')}</li>")
            html.append("</ul>")
            
        # Footer
        html.append(f"<div class='footer'>Generated at {data.get('generated_at')}</div>")
        html.append("</body></html>")
        
        return "\n".join(html)

if __name__ == "__main__":
    # Test stub
    mock_data = {
        "date": "2026-02-01", 
        "summary": {"task_count": 1},
        "priorities": [{"title": "Test Task", "status": "In Progress"}],
        "meeting_summaries": [],
        "flagged_emails": [{"subject": "Urgent", "sender": "Boss"}]
    }
    print(json.dumps(BriefStylizer.to_slack_blocks(mock_data), indent=2))
