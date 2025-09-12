# progress_window.py
import sys
import time
import json
import os
import logging
from enum import Enum
from dataclasses import dataclass
import hashlib
from abc import ABCMeta, abstractmethod
import multiprocessing

def main():
    import multiprocessing
    queue = multiprocessing.Queue(maxsize=10)
    # 这里可以用管道或其他方式接收主进程传来的队列
    while True:
        if not queue.empty():
            progress_data = queue.get()
            if progress_data == "exit":
                break
            percent = progress_data.get("percentage", 0.0)
            desc = progress_data.get("step_description", "处理中")[:40]
calc_logger = logging.getLogger("AdvancedCalculator")

# 2. 定义枚举类型
class NumberCategory(Enum):
    ZERO = 0
    SINGLE_DIGIT = 1
    TEN = 10

# 3. 进度条显示函数（独立进程运行）
def progress_monitor(queue):
    """在新进程中运行的进度条监控器"""
    try:
        # 设置控制台标题
        os.system("title 计算进度监控")
        print("=" * 60)
        print("                      计算进度监控")
        print("=" * 60)
        print("\n提示：关闭此窗口会停止进度显示\n")
        
        while True:
            if not queue.empty():
                progress_data = queue.get()
                if progress_data == "exit":  # 退出信号
                    break
                    
                # 解析进度数据
                percent = progress_data.get("percentage", 0.0)
                desc = progress_data.get("step_description", "处理中")[:40]
                total_steps = progress_data.get("total_steps", 100)
                
                # 渲染进度条
                bar_length = 50
                filled = int(bar_length * (percent / 100))
                bar = '█' * filled + '─' * (bar_length - filled)
                
                # 固定位置刷新进度条
                sys.stdout.write(f"\033[2A\r[{bar}] {percent:.1f}% | 总步骤: {total_steps} | {desc}\033[K\n")
                sys.stdout.write(f"更新时间: {time.strftime('%H:%M:%S')}\033[K\n")
                sys.stdout.flush()
            
            time.sleep(0.1)
            
        print("\n\n进度监控已结束")
        
    except Exception as e:
        print(f"\n\n监控异常: {str(e)}")
        input("按回车关闭窗口...")

# 4. 启动进度监控窗口
def start_progress_window(queue):
    """启动新进程显示进度条（避免代理对象属性访问错误）"""
    import subprocess
    try:
        # 用 start 命令在新窗口运行监控脚本
        monitor_script = os.path.join(os.path.dirname(__file__), "progress_window_monitor.py")
        cmd = f'start "进度监控" python "{monitor_script}"'
        process = subprocess.Popen(cmd, shell=True)
        return process
    except Exception as e:
        print(f"进度窗口启动失败：{str(e)}")
        calc_logger.error(f"进度窗口启动异常：{str(e)}")
        return None

# 5. 进度管理器
class ProgressManager:
    def __init__(self, queue=None):
        self.current_step = 0
        self.total_steps = 100
        self.step_description = "初始化系统"
        self.progress_file = os.path.join(os.path.dirname(__file__), "progress_data.json")

    def set_total_steps(self, total):
        self.total_steps = max(total, 1)
        self.current_step = 0
        self._update_progress()

    def update(self, steps=1, description=None):
        self.current_step = min(self.current_step + steps, self.total_steps)
        if description:
            self.step_description = description
        self._update_progress()

    def reset(self):
        self.current_step = 0
        self.step_description = "初始化系统"
        self._update_progress()

    def _update_progress(self):
        percent = (self.current_step / self.total_steps) * 100
        progress_data = {
            "percentage": round(percent, 1),
            "step_description": self.step_description,
            "total_steps": self.total_steps,
            "timestamp": time.time()
        }
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(progress_data, f)
        except Exception as e:
            pass

# 6. 数据包装类
@dataclass
class NumericValue:
    raw_value: int
    hash: str
    timestamp: float
    category: NumberCategory
    
    def __init__(self, value: int, progress: ProgressManager):
        progress.update(1, "创建数值包装对象")
        self.raw_value = value
        self.timestamp = time.time()
        self.hash = hashlib.sha256(str(value).encode()).hexdigest()
        self.category = self._determine_category(progress)
        calc_logger.debug(f"数值对象创建完成: {self.raw_value}")
        self._simulate_processing(0.3)

    def _determine_category(self, progress: ProgressManager):
        progress.update(1, "分类数值类型")
        self._simulate_processing(0.2)
        if self.raw_value == 0:
            return NumberCategory.ZERO
        elif 1 <= self.raw_value <= 9:
            return NumberCategory.SINGLE_DIGIT
        elif self.raw_value == 10:
            return NumberCategory.TEN
        else:
            raise ValueError(f"无效数值: {self.raw_value}（仅支持0-10）")

    def to_json(self, progress: ProgressManager):
        progress.update(1, "序列化数值为JSON")
        self._simulate_processing(0.1)
        return json.dumps({
            "raw_value": self.raw_value,
            "hash": self.hash,
            "timestamp": self.timestamp,
            "category": self.category.value
        })

    @classmethod
    def from_json(cls, json_str: str, progress: ProgressManager):
        progress.update(1, "反序列化JSON为数值")
        cls._simulate_processing(0.1)
        data = json.loads(json_str)
        obj = cls(data["raw_value"], progress)
        if obj.hash != data["hash"]:
            raise ValueError("数据完整性校验失败")
        return obj

    @staticmethod
    def _simulate_processing(duration: float):
        time.sleep(duration)

# 7. 数据转换管道
class DataTransformationPipeline:
    @staticmethod
    def transform(value: NumericValue, progress: ProgressManager) -> NumericValue:
        progress.set_total_steps(20)
        progress.update(2, "启动数据转换流程")
        
        progress.update(3, "数值转单词描述")
        word_map = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
                   5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
        word = word_map[value.raw_value]
        NumericValue._simulate_processing(0.3)

        progress.update(3, "单词转ASCII编码")
        ascii_codes = [ord(c) for c in word]
        NumericValue._simulate_processing(0.3)

        progress.update(4, "ASCII码校验与数值恢复")
        ascii_sum = sum(ascii_codes)
        recovered = ascii_sum % 11
        NumericValue._simulate_processing(0.4)

        progress.update(3, "创建转换后数值对象")
        result = NumericValue(recovered, progress)
        if result.raw_value != value.raw_value:
            calc_logger.warning("转换偏差自动修正")
            result = NumericValue(value.raw_value, progress)

        progress.update(5, "数据转换流程完成")
        return result

# 8. 数据校验器
class DataValidator:
    @staticmethod
    def validate(value: NumericValue, progress: ProgressManager) -> bool:
        progress.set_total_steps(15)
        progress.update(2, "启动数据校验流程")
        
        progress.update(2, "校验数值类型")
        type_check = isinstance(value.raw_value, int)
        NumericValue._simulate_processing(0.2)

        progress.update(2, "校验数值范围")
        range_check = 0 <= value.raw_value <= 10
        NumericValue._simulate_processing(0.2)

        progress.update(3, "校验数据哈希")
        expected_hash = hashlib.sha256(str(value.raw_value).encode()).hexdigest()
        hash_check = value.hash == expected_hash
        NumericValue._simulate_processing(0.3)

        progress.update(3, "校验数据完整性")
        integrity_check = value.to_json(progress) is not None
        NumericValue._simulate_processing(0.3)

        progress.update(5, "汇总校验结果")
        result = all([type_check, range_check, hash_check, integrity_check])
        NumericValue._simulate_processing(0.2)

        if result:
            calc_logger.info(f"数值{value.raw_value}校验通过")
        else:
            calc_logger.error(f"数值{value.raw_value}校验失败")
        return result

# 9. 运算策略
class OperationStrategy(metaclass=ABCMeta):
    @abstractmethod
    def calculate(self, a: NumericValue, b: NumericValue, progress: ProgressManager) -> NumericValue:
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass

class AddStrategy(OperationStrategy):
    def calculate(self, a: NumericValue, b: NumericValue, progress: ProgressManager) -> NumericValue:
        progress.set_total_steps(30)
        progress.update(5, "初始化加法运算")

        progress.update(8, "拆分第一个数值为单位量")
        a_units = [1 for _ in range(a.raw_value)]
        NumericValue._simulate_processing(0.5)

        progress.update(8, "拆分第二个数值为单位量")
        b_units = [1 for _ in range(b.raw_value)]
        NumericValue._simulate_processing(0.5)

        progress.update(7, "合并单位量并计算总和")
        result = len(a_units + b_units)
        NumericValue._simulate_processing(0.5)

        progress.update(2, "加法结果交叉校验")
        if result != a.raw_value + b.raw_value:
            raise RuntimeError("加法运算异常，结果不匹配")

        progress.update(0, "加法运算完成")
        calc_logger.info(f"加法结果: {a.raw_value} + {b.raw_value} = {result}")
        return NumericValue(result, progress)

    def get_symbol(self) -> str:
        return "+"

class SubtractStrategy(OperationStrategy):
    def calculate(self, a: NumericValue, b: NumericValue, progress: ProgressManager) -> NumericValue:
        progress.set_total_steps(30)
        progress.update(5, "初始化减法运算")

        if a.raw_value < b.raw_value:
            raise ValueError("被减数不能小于减数（仅支持非负结果）")

        progress.set_total_steps(25)
        result = a.raw_value
        step_increment = 20 / b.raw_value if b.raw_value > 0 else 20

        for i in range(b.raw_value):
            result -= 1
            progress.update(step_increment, f"减法步骤 {i+1}/{b.raw_value}")
            NumericValue._simulate_processing(0.3)

        progress.update(5, "减法结果交叉校验")
        if result != a.raw_value - b.raw_value:
            raise RuntimeError("减法运算异常，结果不匹配")

        progress.update(0, "减法运算完成")
        calc_logger.info(f"减法结果: {a.raw_value} - {b.raw_value} = {result}")
        return NumericValue(result, progress)

    def get_symbol(self) -> str:
        return "-"

# 10. 运算上下文
class OperationContext:
    def __init__(self, strategy: OperationStrategy, progress: ProgressManager):
        self.strategy = strategy
        self.progress = progress
        self.history = []

    def execute(self, a: int, b: int) -> int:
        self.progress.reset()
        self.progress.set_total_steps(100)

        self.progress.update(10, "接收运算参数并封装")
        a_val = NumericValue(a, self.progress)
        b_val = NumericValue(b, self.progress)

        self.progress.update(20, "启动数据合法性校验")
        if not (DataValidator.validate(a_val, self.progress) and DataValidator.validate(b_val, self.progress)):
            raise ValueError("输入数据校验失败，无法继续运算")

        self.progress.update(25, "启动数据预处理转换")
        a_trans = DataTransformationPipeline.transform(a_val, self.progress)
        b_trans = DataTransformationPipeline.transform(b_val, self.progress)

        self.progress.update(35, "执行核心运算逻辑")
        result_val = self.strategy.calculate(a_trans, b_trans, self.progress)

        self.progress.update(10, "整理运算结果并记录")
        self.history.append({
            "a": a, "b": b, "op": self.strategy.get_symbol(),
            "result": result_val.raw_value, "time": time.strftime("%H:%M:%S")
        })

        self.progress.update(100, "运算流程全部完成")
        return result_val.raw_value

# 11. 计算器核心
class CalculatorCore:
    def __init__(self, shared_queue):
        self.progress = ProgressManager(shared_queue)
        self.strategies = {
            "+": AddStrategy(),
            "-": SubtractStrategy()
        }
        self.context = None
        calc_logger.info("计算器核心初始化完成")

    def set_operation(self, op_symbol: str):
        if op_symbol not in self.strategies:
            raise ValueError(f"不支持的运算符：{op_symbol}（仅支持+、-）")
        self.context = OperationContext(self.strategies[op_symbol], self.progress)
        self.progress.update(0, f"已选择运算类型：{op_symbol}")

    def compute(self, a: int, b: int) -> int:
        if not self.context:
            raise RuntimeError("未选择运算类型，请先输入合法运算符（+/-）")
        return self.context.execute(a, b)

    def get_history(self) -> list:
        return self.context.history if self.context else []

# 12. 用户交互界面
class CalculatorUI:
    def __init__(self, shared_queue, progress_process):
        self.core = CalculatorCore(shared_queue)
        self.progress_process = progress_process
        self.welcome_msg = (
            "============================================\n"
            "          十以内加减法计算器（v2.0）          \n"
            "============================================\n"
            "支持运算：加法(+)、减法(-)\n"
            "输入格式：数字 运算符 数字（例如：3 + 5）\n"
            "输入 'exit' 退出程序\n"
            "输入 'history' 查看历史记录\n"
        )

    def _parse_input(self, user_input: str) -> tuple:
        user_input = user_input.strip()
        
        if user_input.lower() == "exit":
            return ("exit", None)
        if user_input.lower() == "history":
            return ("history", None)
        
        parts = user_input.split()
        if len(parts) != 3:
            raise ValueError("输入格式错误，请使用：数字 运算符 数字（例：5 - 2）")
        
        try:
            a = int(parts[0])
            op = parts[1]
            b = int(parts[2])
            return ("calculate", (a, op, b))
        except ValueError:
            raise ValueError("无效的数字，请输入0-10之间的整数")

    def run(self):
        print(self.welcome_msg)
        
        try:
            while True:
                user_input = input("请输入运算表达式：")
                command, data = self._parse_input(user_input)
                
                if command == "exit":
                    print("感谢使用计算器，再见！")
                    break
                elif command == "history":
                    history = self.core.get_history()
                    if not history:
                        print("暂无运算记录\n")
                    else:
                        print("运算历史记录：")
                        for i, item in enumerate(history, 1):
                            print(f"  {i}. {item['a']} {item['op']} {item['b']} = {item['result']} （{item['time']}）")
                        print()
                elif command == "calculate":
                    a, op, b = data
                    print(f"正在执行计算：{a} {op} {b}（进度请查看监控窗口）")
                    
                    self.core.set_operation(op)
                    result = self.core.compute(a, b)
                    print(f"计算完成！结果：{a} {op} {b} = {result}\n")
        
        finally:
            # 退出时终止进度进程（用 poll 判断 Popen 是否存活）
            if self.progress_process and hasattr(self.progress_process, "poll") and self.progress_process.poll() is None:
                progress_file = os.path.join(os.path.dirname(__file__), "progress_data.json")
                try:
                    import json
                    with open(progress_file, "w", encoding="utf-8") as f:
                        json.dump("exit", f)
                except Exception:
                    pass

# 13. 主程序入口
def main():
    try:
        # 1. 创建共享队列（使用普通Queue而非Manager.Queue）
        shared_queue = multiprocessing.Queue(maxsize=10)
        
        # 2. 启动进度监控进程
        print("正在启动进度监控窗口...")
        progress_process = start_progress_window(shared_queue)
        if not progress_process:
            print("无法启动进度窗口，程序将继续运行但无进度显示")
        
        # 等待进度窗口启动
        time.sleep(1)
        
        # 3. 启动用户交互界面
        ui = CalculatorUI(shared_queue, progress_process)
        ui.run()
    except Exception as e:
        print(f"程序启动失败：{str(e)}")
        calc_logger.error(f"主程序启动异常：{str(e)}")
        input("按回车关闭...")

if __name__ == "__main__":
    # Windows系统多进程支持
    if os.name == 'nt':
        multiprocessing.freeze_support()
    main()
