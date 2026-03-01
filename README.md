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
  "app_password": "your-app-password",
  "user_id": "your-user-id",
  "calendars": {
    "工作": "日历ID",
    "家庭日历": "日历ID"
  }
}
```

### 2. 获取 App Specific Password

1. 登录 https://appleid.apple.com
2. 前往「安全」→「专用密码」
3. 生成新密码

### 3. 获取 user_id

运行以下命令获取 user_id：

```bash
curl -s -u "your@icloud.email:your-app-password" https://caldav.icloud.com/
```

输出示例：
```xml
<multistatus>
  <response>
    <href>/<YOUR_USER_ID>/calendars/</href>
  </response>
</multistatus>
```

**user_id 就是 URL 中的数字**：<YOUR_USER_ID>

### 4. 获取日历 ID

运行以下命令获取：

```bash
python3 ~/.openclaw/scripts/icloud_calendar.py calendars
```

输出格式：
```json
{
  "工作": "005D6E33-C41E-4D33-AAA8-8C169B69B27E",
  "家庭日历": "489BCDE4-8FAA-4A7F-9791-6FD2E6516D32"
}
```

将输出的 ID 填入配置文件的 calendars 字段。

## 使用

```bash
# 获取最近30分钟事件
python3 ~/.openclaw/scripts/icloud_calendar.py upcoming

# 获取今日事件
python3 ~/.openclaw/scripts/icloud_calendar.py today

# 获取未来7天事件
python3 ~/.openclaw/scripts/icloud_calendar.py list

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
