import inspect
import your_module  # 替换为实际模块

# 生成 .pyi 文件
with open("your_module.pyi", "w") as f:
    for name, obj in inspect.getmembers(your_module):
        if inspect.isclass(obj) and not name.startswith("_"):
            f.write(f"class {name}:\n")
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                if not method_name.startswith("_"):
                    signature = inspect.signature(method)
                    f.write(f"    def {method_name}{signature}: ...\n")
        elif inspect.isfunction(obj) and not name.startswith("_"):
            signature = inspect.signature(obj)
            f.write(f"def {name}{signature}: ...\n")


import re

def process_pyi_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    with open(file_path, "w") as file:
        inside_class = False
        for line in lines:
            if line.startswith("class "):
                inside_class = True
                # 仅保留类名，不保留内部定义
                file.write(line)
            elif inside_class and line.strip() == "":
                inside_class = False
                file.write(line)
            elif not inside_class:
                file.write(line)
            # 过滤掉类内的属性和方法
            elif inside_class and not (line.startswith("    def ") or line.startswith("    @")):
                file.write(line)

# 处理指定的 .pyi 文件
process_pyi_file("your_module.pyi")
