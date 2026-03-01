# iCloud Calendar Skill

> 通过 CalDAV 协议访问 iCloud 日历

## 功能

- 读取日历事件
- 获取日历提醒
- 添加日程

## 安装

```bash
cp icloud_calendar.py ~/.openclaw/scripts/
```

## 配置

创建 `~/.openclaw/conf/icloud-calendar/config.json`：

```json
{
  "apple_id": "your@icloud.email",
  "app_password": "your-app-password",
  "user_id": "your-user-id",
  "calendars": {
    "工作": "日历ID",
    "家庭日历": "日历ID"
  }
}
```

## 使用

```bash
python3 ~/.openclaw/scripts/icloud_calendar.py upcoming  # 最近30分钟
python3 ~/.openclaw/scripts/icloud_calendar.py today    # 今日事件
python3 ~/.openclaw/scripts/icloud_calendar.py add "标题" 30  # 添加日程
```

## License

MIT
