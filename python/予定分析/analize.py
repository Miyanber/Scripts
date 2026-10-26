#!/usr/bin/env python3
from datetime import datetime, timedelta
from collections import defaultdict

# 各タスクの情報を定義（所要時間は分単位で管理）
# サンプルデータです。必要に応じて書き換えてください。
tasks = [
    # 物理
    {"name": "物理 基本問題330~331", "time": 2 * 7, "deadline": "2025-05-26"},
    {"name": "物理 発展問題332~337", "time": 6 * 15, "deadline": "2025-05-26"},
    {"name": "物理 演習問題 88~105", "time": 21 * 16, "deadline": "2025-05-26"},
    {"name": "物理 重要問題演習", "time": 20 * 16, "deadline": "2025-05-31"},
    # 化学
    {"name": "化学 基本問題302~312", "time": 11 * 7, "deadline": "2025-05-26"},
    {"name": "化学 応用問題313~325", "time": 13 * 12, "deadline": "2025-05-26"},
    {"name": "化学 テスト勉強", "time": 2 * 60, "deadline": "2025-05-26"},
    {"name": "化学 復習 No.6", "time": 2 * 60, "deadline": "2025-05-21"},
    {"name": "化学 予習 No.7", "time": 1.5 * 60, "deadline": "2025-05-21"},
    {"name": "化学 復習 No.7", "time": 2 * 60, "deadline": "2025-05-28"},
    {"name": "化学 予習 No.8", "time": 1.5 * 60, "deadline": "2025-05-28"},
    {"name": "化学 解き直し No.3", "time": 60, "deadline": "2025-05-31"},
    {"name": "化学 解き直し No.4", "time": 60, "deadline": "2025-05-31"},
    {"name": "化学 解き直し No.5", "time": 60, "deadline": "2025-05-31"},
    # 数学
    {"name": "数学 単元別演習 No.6", "time": 4 * 60, "deadline": "2025-05-27"},
    {"name": "数学 単元別演習 No.7", "time": 4 * 60, "deadline": "2025-05-30"},
    {"name": "数学 極限演習", "time": 2 * 60, "deadline": "2025-05-23"},
    {"name": "数学 実践問題復習", "time": 2 * 60, "deadline": "2025-05-23"},
    # 英語
    {"name": "英語 論理表現演習", "time": 3 * 60, "deadline": "2025-05-22"},
    {"name": "英語 長文読解 Chapter2,4", "time": 2 * 60, "deadline": "2025-05-22"},
    {"name": "英語 リーディング演習", "time": 2 * 60, "deadline": "2025-05-22"},
    {"name": "英語 コミュニケーション演習", "time": 2 * 60, "deadline": "2025-05-22"},
    # 国語
    {"name": "古典 復習", "time": 2 * 60, "deadline": "2025-05-22"},
    {"name": "現代文 演習", "time": 2 * 60, "deadline": "2025-05-22"},
]


# 空き時間（h→分）
free_time = {
    "2025-05-19": 3 * 60,
    "2025-05-20": 2 * 60,
    "2025-05-21": 7 * 60,
    "2025-05-22": 4 * 60,
    "2025-05-23": 7 * 60,
    "2025-05-24": 1 * 60,
    "2025-05-25": 10 * 60,
    "2025-05-26": 6.5 * 60,
    "2025-05-27": 2 * 60,
    "2025-05-28": 4 * 60,
    "2025-05-29": 3 * 60,
    "2025-05-30": 0,
    "2025-05-31": 2 * 60,
}

# 合計時間を確認するために、タスクを要約する
total_task_time = sum(task["time"] for task in tasks)
total_free_time = sum(free_time.values())

total_task_time, total_free_time, total_task_time - total_free_time




### 分析後半




# 日付ごとのスケジュールを作成する
from datetime import datetime

# 日付文字列を日付型に変換する関数
def to_date(d):
    return datetime.strptime(d, "%Y-%m-%d").date()

# タスクを優先度と期限でソート（優先度高い順 → 期限早い順）
sorted_tasks = sorted(
    tasks,
    key=lambda x: (not x.get("priority", False), to_date(x["deadline"]))
)


# 日付ごとのスケジュール格納先（分単位）
schedule = defaultdict(list)
remaining_time = free_time.copy()

# タスク割り当て結果と未割当タスク
unassigned_tasks = []
for task in sorted_tasks:
    time_left = task["time"]
    deadline = to_date(task["deadline"])
    assigned = False

    for day in sorted(remaining_time):
        day_date = to_date(day)
        if day_date <= deadline and time_left > 0:
            available = remaining_time[day]
            if available > 0:
                # 割り当てる時間（休憩込み、1コマ最大180分）
                assign = min(available, time_left, 180)
                schedule[day].append((task["name"], assign))
                remaining_time[day] -= assign
                time_left -= assign

    if time_left > 0:
        unassigned_tasks.append((task["name"], time_left))

schedule, unassigned_tasks

# スケジュールを表示
def print_schedule(schedule):
    for date, tasks in schedule.items():
        print(f"{date}:")
        for task, time in tasks:
            print(f"  {task}: {time}分")
        print()

print_schedule(schedule)

# 未割当タスクを表示
def print_unassigned_tasks(unassigned_tasks):
    if unassigned_tasks:
        print("未割当タスク:")
        for task, time in unassigned_tasks:
            print(f"  {task}: {time}分")
    else:
        print("すべてのタスクが割り当てられました。")

print_unassigned_tasks(unassigned_tasks)