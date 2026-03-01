# iCloud Calendar Skill

> 通过 CalDAV 协议访问 iCloud 日历

## 功能

- 读取日历事件
- 获取日历提醒
- 添加日程

## 安装

```bash
cp icloud_calendar.py ~/.openclaw/scripts/
mkdir -p ~/.openclaw/conf/icloud-calendar
cp config.example.json ~/.openclaw/conf/icloud-calendar/config.json
```

## 配置

### 1. 编辑配置文件

编辑 `~/.openclaw/conf/icloud-calendar/config.json`：

```json
{
  "apple_id": "your@icloud.email",
  "app_password": "app-specific-password",
  "user_id": "0012345678",
  "calendars": {
    "工作": "工作日历ID",
    "家庭日历": "家庭日历ID"
  }
}
```

### 2. 获取 App Specific Password

1. 登录 https://appleid.apple.com
2. 前往「安全」→「专用密码」
3. 生成新密码

## 使用

```bash
# 获取最近30分钟事件
python3 ~/.openclaw/scripts/icloud_calendar.py upcoming

# 获取今日事件
python3 ~/.openclaw/scripts/icloud_calendar.py today

# 获取未来7天事件
python3 ~/.openclaw/scripts/icloud_calendar.py list

# 获取日历 ID
python3 ~/.openclaw/scripts/icloud_calendar.py calendars

# 添加日程（30分钟后提醒）
python3 ~/.openclaw/scripts/icloud_calendar.py add "喝水提醒" 30
```

## 输出示例

```json
{
  "upcoming": [
    {
      "summary": "喝水提醒",
      "time": "03-01 19:30",
      "minutes_until": 25,
      "calendar": "家庭日历"
    }
  ]
}
```

## License

MIT
