#!/usr/bin/env python3
"""
iCloud Calendar 访问脚本
用法: 
  python3 icloud_calendar.py list        # 列出所有事件（未来7天）
  python3 icloud_calendar.py upcoming   # 获取最近30分钟事件
  python3 icloud_calendar.py today      # 获取今日事件
  python3 icloud_calendar.py calendars   # 获取日历列表（包含ID）
  python3 icloud_calendar.py add <标题> [分钟数]  # 添加日程
"""

import json
import subprocess
import sys
import os
import re
from datetime import datetime, timedelta
import uuid

# ====== 配置 ======
CONFIG_DIR = os.path.expanduser("~/.openclaw/conf/icloud-calendar")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
CALDAV_URL = "https://caldav.icloud.com"

# 全局变量
config = {}
USER_ID = None
CALENDARS = {}

def load_config():
    global config, USER_ID, CALENDARS
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        USER_ID = config.get("user_id", "")
        CALENDARS = config.get("calendars", {})
        return True
    return False

# 加载配置
if not load_config():
    print("错误: 配置文件不存在，请先创建 ~/.openclaw/conf/icloud-calendar/config.json")
    sys.exit(1)

apple_id = config.get("apple_id", "")
app_password = config.get("app_password", "")

def run_curl(method, url, data=None, headers=None, check_returncode=False):
    cmd = ["curl", "-s", "-X", method, url, "-u", f"{apple_id}:{app_password}"]
    if headers:
        for h in headers:
            cmd.extend(["-H", h])
    if data:
        cmd.extend(["-d", data])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if check_returncode:
        return result.returncode == 0
    return result.stdout

def query_calendar_events(cal_id, start_offset_hours=-1, end_offset_days=7):
    """查询日历事件"""
    url = f"{CALDAV_URL}/{USER_ID}/calendars/{cal_id}"
    
    now = datetime.now()
    start = (now + timedelta(hours=start_offset_hours)).strftime("%Y%m%dT%H%M%SZ")
    end = (now + timedelta(days=end_offset_days)).strftime("%Y%m%dT%H%M%SZ")
    
    data = f'''<?xml version="1.0" encoding="UTF-8"?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop><c:calendar-data/></d:prop>
  <c:filter><c:comp-filter name="VCALENDAR"/></c:filter>
</c:calendar-query>'''
    
    result = run_curl("REPORT", url, data=data, headers=["Content-Type: application/xml; charset=utf-8", "Depth: 1"])
    return result

def parse_events(result, now, filter_minutes=30):
    """解析事件"""
    events = []
    lines = result.split('\n')
    current_event = {}
    in_vevent = False
    
    for line in lines:
        # 检测 VEVENT 边界
        if 'BEGIN:VEVENT' in line:
            in_vevent = True
            current_event = {}
            continue
        if 'END:VEVENT' in line:
            in_vevent = False
            if current_event.get('dtstart') and current_event.get('summary'):
                try:
                    dt = datetime.strptime(current_event['dtstart'], "%Y%m%dT%H%M")
                    diff = (dt - now).total_seconds() / 60
                    current_event['time'] = current_event['dtstart'][4:6] + '-' + current_event['dtstart'][6:8] + ' ' + current_event['dtstart'][9:11] + ':' + current_event['dtstart'][11:13]
                    current_event['minutes_until'] = int(diff)
                    
                    if 0 <= diff < filter_minutes:
                        events.append({
                            'summary': current_event['summary'],
                            'time': current_event['time'],
                            'minutes_until': int(diff),
                            'calendar': current_event.get('calendar', '未知')
                        })
                except:
                    pass
            current_event = {}
            continue
        
        if not in_vevent:
            continue
            
        if 'DTSTART' in line:
            # 支持带时区和不带时区的时间格式: DTSTART;TZID=Asia/Shanghai:20260301T215753 或 DTSTART:20260301T2157
            match = re.search(r'DTSTART[^:]*:(\d{8}T\d{2,6})', line)
            if match:
                dt_str = match.group(1)
                # YYYYMMDDTHHMM = 13位
                current_event['dtstart'] = dt_str[:13]
        if 'SUMMARY' in line:
            match = re.search(r'SUMMARY:([^\r\n]+)', line)
            if match:
                current_event['summary'] = match.group(1).strip()
    
    return events

def list_calendars():
    """列出所有日历 - 从配置读取"""
    # 从配置文件读取日历映射
    print(json.dumps(CALENDARS, indent=2, ensure_ascii=False))
    return CALENDARS

def cmd_list():
    """列出所有事件（未来7天）"""
    now = datetime.now()
    all_events = []
    
    for cal_name, cal_id in CALENDARS.items():
        result = query_calendar_events(cal_id, start_offset_hours=-24, end_offset_days=7)
        events = parse_events(result, now, filter_minutes=10080)  # 7天
        for e in events:
            e['calendar'] = cal_name
            all_events.append(e)
    
    # 按时间排序
    all_events.sort(key=lambda x: x.get('minutes_until', 99999))
    print(json.dumps({"events": all_events[:20]}, indent=2, ensure_ascii=False))

def cmd_upcoming():
    """获取最近30分钟事件"""
    now = datetime.now()
    all_events = []
    
    for cal_name, cal_id in CALENDARS.items():
        result = query_calendar_events(cal_id, start_offset_hours=-1, end_offset_days=1)
        events = parse_events(result, now, filter_minutes=30)
        for e in events:
            e['calendar'] = cal_name
            all_events.append(e)
    
    # 按时间排序
    all_events.sort(key=lambda x: x.get('minutes_until', 99999))
    print(json.dumps({"upcoming": all_events}, indent=2, ensure_ascii=False))

def cmd_today():
    """获取今日事件"""
    now = datetime.now()
    # 计算今天剩余分钟数
    today_end = datetime(now.year, now.month, now.day, 23, 59)
    filter_minutes = int((today_end - now).total_seconds() / 60)
    
    all_events = []
    
    for cal_name, cal_id in CALENDARS.items():
        result = query_calendar_events(cal_id, start_offset_hours=-1, end_offset_days=1)
        events = parse_events(result, now, filter_minutes=filter_minutes)
        for e in events:
            e['calendar'] = cal_name
            all_events.append(e)
    
    all_events.sort(key=lambda x: x.get('minutes_until', 99999))
    print(json.dumps({"today": all_events}, indent=2, ensure_ascii=False))

def cmd_add(summary, description="", minutes=20):
    """添加日程"""
    # 默认添加到"家庭日历"
    calendar_name = config.get("default_calendar", "") or (list(CALENDARS.keys())[0] if CALENDARS else "")
    cal_id = CALENDARS.get(calendar_name, "")
    
    if not cal_id:
        return {"error": f"日历不存在: {calendar_name}"}
    
    # 计算时间
    start_time = datetime.now() + timedelta(minutes=minutes)
    end_time = start_time + timedelta(minutes=20)
    
    # 生成唯一ID
    event_uid = str(uuid.uuid4())
    
    # 构建 iCal 格式
    ical = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;TZID=Asia/Shanghai:{start_time.strftime("%Y%m%dT%H%M%S")}
DTEND;TZID=Asia/Shanghai:{end_time.strftime("%Y%m%dT%H%M%S")}
SUMMARY:{summary}
DESCRIPTION:{description}
UID:{event_uid}
END:VEVENT
END:VCALENDAR"""
    
    url = f"{CALDAV_URL}/{USER_ID}/calendars/{cal_id}/{event_uid}.ics"
    
    result = run_curl("PUT", url, data=ical, headers=["Content-Type: text/calendar; charset=utf-8"])
    
    return {"success": True, "message": f"已添加到 {calendar_name}: {summary}", "time": start_time.strftime("%H:%M"), "uid": event_uid}

def parse_events_with_uid(result, now):
    """解析事件（包含UID）"""
    events = []
    lines = result.split('\n')
    current_event = {}
    in_vevent = False
    
    for line in lines:
        # 检测 VEVENT 边界
        if 'BEGIN:VEVENT' in line:
            in_vevent = True
            current_event = {}
            continue
        if 'END:VEVENT' in line:
            in_vevent = False
            # VEVENT 结束时，检查是否有完整事件
            if current_event.get('dtstart') and current_event.get('uid') and current_event.get('summary'):
                try:
                    dt = datetime.strptime(current_event['dtstart'], "%Y%m%dT%H%M")
                    current_event['minutes_until'] = int((dt - now).total_seconds() / 60)
                    events.append(current_event.copy())
                except:
                    pass
            current_event = {}
            continue
        
        if not in_vevent:
            continue
            
        if 'UID:' in line:
            match = re.search(r'UID:([^\r\n]+)', line)
            if match:
                current_event['uid'] = match.group(1).strip()
        if 'DTSTART' in line:
            # 支持带时区和不带时区的时间格式
            match = re.search(r'DTSTART[^:]*:(\d{8}T\d{2,6})', line)
            if match:
                dt_str = match.group(1)
                current_event['dtstart'] = dt_str[:13]
        if 'SUMMARY' in line:
            match = re.search(r'SUMMARY:([^\r\n]+)', line)
            if match:
                current_event['summary'] = match.group(1).strip()
    
    return events

def cmd_delete(identifier, calendar_name=None):
    """删除日程 - 通过标题或UID删除"""
    calendars_to_search = {}
    if calendar_name:
        cal_id = CALENDARS.get(calendar_name, "")
        if not cal_id:
            return {"error": f"日历不存在: {calendar_name}"}
        calendars_to_search = {calendar_name: cal_id}
    else:
        calendars_to_search = CALENDARS
    
    now = datetime.now()
    
    # 先尝试作为 UID 直接删除（只有当 identifier 看起来像 UUID 格式时才尝试）
    uuid_pattern = re.compile(r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$', re.I)
    if uuid_pattern.match(identifier):
        for cal_name, cal_id in calendars_to_search.items():
            url = f"{CALDAV_URL}/{USER_ID}/calendars/{cal_id}/{identifier}.ics"
            if run_curl("DELETE", url, check_returncode=True):
                return {"success": True, "message": f"已删除事件 (UID): {identifier}", "calendar": cal_name}
    
    # 作为标题搜索并删除最近的匹配事件
    for cal_name, cal_id in calendars_to_search.items():
        result = query_calendar_events(cal_id, start_offset_hours=-24, end_offset_days=7)
        events = parse_events_with_uid(result, now)
        
        for event in events:
            if identifier.lower() in event.get('summary', '').lower():
                event_uid = event.get('uid', '')
                if event_uid:
                    url = f"{CALDAV_URL}/{USER_ID}/calendars/{cal_id}/{event_uid}.ics"
                    if run_curl("DELETE", url, check_returncode=True):
                        return {"success": True, "message": f"已删除事件: {event['summary']}", "calendar": cal_name}
    
    return {"error": f"未找到事件: {identifier}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 icloud_calendar.py list          # 列出所有事件（未来7天）")
        print("  python3 icloud_calendar.py upcoming     # 获取最近30分钟事件")
        print("  python3 icloud_calendar.py today         # 获取今日事件")
        print("  python3 icloud_calendar.py calendars     # 获取日历列表")
        print("  python3 icloud_calendar.py add <标题> [分钟数]  # 添加日程")
        print("  python3 icloud_calendar.py delete <标题或UID> [日历名]  # 删除日程")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        cmd_list()
    elif cmd == "upcoming":
        cmd_upcoming()
    elif cmd == "today":
        cmd_today()
    elif cmd == "calendars":
        list_calendars()
    elif cmd == "add":
        summary = sys.argv[2] if len(sys.argv) > 2 else "新日程"
        minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        result = cmd_add(summary, "", minutes)
        print(json.dumps(result, ensure_ascii=False))
    elif cmd == "delete":
        identifier = sys.argv[2] if len(sys.argv) > 2 else ""
        calendar_name = sys.argv[3] if len(sys.argv) > 3 else None
        if not identifier:
            print("错误: 请提供要删除的事件标题或UID")
            sys.exit(1)
        result = cmd_delete(identifier, calendar_name)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
