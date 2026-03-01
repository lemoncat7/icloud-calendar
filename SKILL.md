---
name: icloud-calendar
description: "Access iCloud Calendar via CalDAV. Use for: (1) Reading calendar events, (2) Getting upcoming reminders, (3) Adding events. Requires config with apple_id, app_password, user_id, and calendar IDs."
metadata:
  - Calendar
  - iCloud
  - Reminder
---

# iCloud Calendar Skill

Access iCloud Calendar via CalDAV protocol.

## Quick Reference

| Command | Description |
|---------|-------------|
| `icloud_calendar.py upcoming` | Get events in next 30 minutes |
| `icloud_calendar.py today` | Get today's events |
| `icloud_calendar.py list` | Get events for next 7 days |
| `icloud_calendar.py add "Title" 30` | Add event in 30 minutes |

## Installation

1. Copy script: `cp icloud_calendar.py ~/.openclaw/scripts/`
2. Create config: `~/.openclaw/conf/icloud-calendar/config.json`

## Configuration

```json
{
  "apple_id": "your@email",
  "app_password": "app-specific-password",
  "user_id": "your-icloud-user-id",
  "calendars": {
    "工作": "calendar-id",
    "家庭日历": "calendar-id"
  }
}
```

## Setup

1. Get App Specific Password from appleid.apple.com
2. Find user_id and calendar IDs using `icloud_calendar.py calendars`

## Usage in OpenClaw

```bash
# Check upcoming events
python3 ~/.openclaw/scripts/icloud_calendar.py upcoming

# Add reminder
python3 ~/.openclaw/scripts/icloud_calendar.py add "喝水" 30
```
