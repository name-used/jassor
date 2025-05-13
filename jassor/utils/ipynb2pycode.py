import os.path

import nbformat


def ipynb2pycode(ipynb: str) -> str:
    # 可以输入 path，也可以直接输入文件内容
    if os.path.exists(ipynb):
        nb = nbformat.read(ipynb, as_version=4)
    else:
        nb = nbformat.reads(ipynb, as_version=4)
    lines = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            code = cell.source
            for line in code.splitlines():
                stripped = line.strip()
                if not stripped.startswith('#') and stripped != '':
                    lines.append(line)
    return '\n'.join(lines)
