from typing import Any
import json


class JassorJsonEncoder(json.JSONEncoder):
    # 只支持 dict、list、tuple、str、number 且 dict 的 key 必须是 str
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(*args)
        # print(list(kwargs.items()))
        self.indent = kwargs['indent'] or 4
        self.count = 0

    def encode(self, obj: Any) -> str:
        if isinstance(obj, (list, tuple)) and all(map(lambda x: not isinstance(x, (list, tuple, dict)), obj)) or \
                isinstance(obj, dict) and all(map(lambda v: not isinstance(v, (list, tuple, dict)), obj.values())):
            json_str = json.dumps(obj)
        elif isinstance(obj, dict):
            end = '\n' + ' ' * self.count + '}'
            self.count += self.indent
            head = '{\n' + ' ' * self.count
            transer = lambda kv: f'"{str(kv[0])}": {self.encode(kv[1])}'
            content = f',\n{" " * self.count}'.join(map(transer, obj.items()))
            self.count -= self.indent
            json_str = head + content + end
        elif isinstance(obj, (list, tuple)):
            end = '\n' + ' ' * self.count + ']'
            self.count += self.indent
            head = '[\n' + ' ' * self.count
            content = f',\n{" " * self.count}'.join(map(self.encode, obj))
            self.count -= self.indent
            json_str = head + content + end
        else:
            json_str = json.dumps(obj)
        return json_str

    def iterencode(self, o, _one_shot=False):
        return self.encode(o)
