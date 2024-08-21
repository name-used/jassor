import json
from jassor.utils import JassorJsonEncoder

x = [{1: 2}, [1, 2, 3], [1, 2, [3, 4, 5], {'fdafad': 12314}], (), (1,2,3,4)]
# print(json.dumps(x, cls=JassorJsonEncoder))
# print(json.dumps(x, indent=4))
with open('../../output/test_output.json', 'w') as f:
    # json.dump(x, f)
    json.dump(x, f, cls=JassorJsonEncoder)
