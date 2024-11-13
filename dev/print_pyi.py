import inspect
import typing
import jassor.utils.table


def main():
    print(generate_pyi(jassor.utils.table))


def type_to_str(t):
    """Convert a type to a .pyi-compatible string."""
    # 处理 Union 类型 (e.g., Union[int, str] -> int | str)
    if getattr(t, "__origin__", None) is typing.Union:
        return " | ".join(type_to_str(arg) for arg in t.__args__)
    # 特殊处理常见的类型
    elif t is typing.Any:
        return "Any"
    elif t is typing.Callable:
        return "Callable"
    elif isinstance(t, type):
        # 提取内置类型名称，如 int, str 等
        return t.__name__
    elif hasattr(t, "__name__"):
        return t.__name__
    return str(t)  # 默认转换


def format_signature(sig):
    """Format a function signature to .pyi-compatible format."""
    parameters = []
    for name, param in sig.parameters.items():
        # 为每个参数生成类型注解
        if param.annotation is param.empty:
            parameters.append(name)
        else:
            parameters.append(f"{name}: {type_to_str(param.annotation)}")
    # 生成返回值类型
    return_type = type_to_str(sig.return_annotation) if sig.return_annotation is not sig.empty else "Any"
    return f"({', '.join(parameters)}) -> {return_type}"


def generate_pyi(module):
    lines = ["from typing import Any, Callable"]  # 引入需要的 typing 类型
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            lines.append(f"class {name}:")
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                sig = inspect.signature(method)
                lines.append(f"    def {method_name}{format_signature(sig)}: ...")
            lines.append("")
        elif inspect.isfunction(obj):
            sig = inspect.signature(obj)
            lines.append(f"def {name}{format_signature(sig)}: ...")
        elif not name.startswith("_"):  # 忽略私有变量
            # 全局变量类型推断
            lines.append(f"{name}: {type_to_str(type(obj))}")
    return "\n".join(lines)


main()
