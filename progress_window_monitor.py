import sys
import time
import json
import os

PROGRESS_FILE = "progress_data.json"

def progress_monitor():
    os.system("title 计算进度监控")
    print("=" * 60)
    print("                      计算进度监控")
    print("=" * 60)
    print("\n提示：关闭此窗口会停止进度显示\n")
    last_data = None
    while True:
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                    try:
                        progress_data = json.load(f)
                    except Exception:
                        progress_data = None
                if progress_data and progress_data != last_data:
                    last_data = progress_data
                    if progress_data == "exit":
                        break
                    percent = progress_data.get("percentage", 0.0)
                    desc = progress_data.get("step_description", "处理中")[:40]
                    total_steps = progress_data.get("total_steps", 100)
                    bar_length = 50
                    filled = int(bar_length * (percent / 100))
                    bar = '█' * filled + '─' * (bar_length - filled)
                    sys.stdout.write(f"\033[2A\r[{bar}] {percent:.1f}% | 总步骤: {total_steps} | {desc}\033[K\n")
                    sys.stdout.write(f"更新时间: {time.strftime('%H:%M:%S')}\033[K\n")
                    sys.stdout.flush()
            time.sleep(0.2)
        except Exception as e:
            print(f"监控异常: {str(e)}")
            time.sleep(1)
    print("\n\n进度监控已结束")
    input("按回车关闭窗口...")

if __name__ == "__main__":
    progress_monitor()
