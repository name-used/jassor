# run cmd with: stubgen -p jassor.utils
import os
from pathlib import Path


root = Path('../out/jassor/utils').absolute()

imports_line = []
content_line = []
for fname in os.listdir(root):
    if fname == '__init__.pyi': continue
    if not fname.endswith('.pyi'): continue
    with open(root / fname, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line.startswith('import') or line.startswith('from'):
                imports_line.append(line)
            else:
                content_line.append(line)

with open(root / '__init__.pyi', 'w') as f:
    f.writelines(imports_line)
    f.writelines(content_line)
