import json

dumped = json.dumps({'key': 'value'}) # '{"key": "value"}'
loaded = json.loads(dumped) # {'key': 'value'}