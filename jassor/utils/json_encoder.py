from typing import Any
import json


class JassorJsonEncoder(json.JSONEncoder):
    # 只支持 dict、list、tuple、str、number 且 dict 的 key 必须是 str
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(*args)
        # print(list(kwargs.items()))
        self._indent = kwargs['indent'] or 4
        self._count = 0

    def encode(self, obj: Any) -> str:
        if isinstance(obj, (list, tuple)) and all(map(lambda x: not isinstance(x, (list, tuple, dict)), obj)) or \
                isinstance(obj, dict) and all(map(lambda v: not isinstance(v, (list, tuple, dict)), obj.values())):
            json_str = json.dumps(obj)
        elif isinstance(obj, dict):
            end = '\n' + ' ' * self._count + '}'
            self._count += self._indent
            head = '{\n' + ' ' * self._count
            transer = lambda kv: f'"{str(kv[0])}": {self.encode(kv[1])}'
            content = f',\n{" " * self._count}'.join(map(transer, obj.items()))
            self._count -= self._indent
            json_str = head + content + end
        elif isinstance(obj, (list, tuple)):
            end = '\n' + ' ' * self._count + ']'
            self._count += self._indent
            head = '[\n' + ' ' * self._count
            content = f',\n{" " * self._count}'.join(map(self.encode, obj))
            self._count -= self._indent
            json_str = head + content + end
        else:
            json_str = json.dumps(obj)
        return json_str

    def iterencode(self, o, _one_shot=False):
        return self.encode(o)
