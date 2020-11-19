from os import listdir
from os.path import isfile, join
import json
import pandas as pd
from jsonschema import exceptions
from jsonschema import validate
from jsonschema import Draft6Validator
from jsonschema import Draft7Validator

with open('task_folder/schema/cmarker_created.schema', 'r') as f:
	schema = json.load(f)

schema_path = 'task_folder/schema/'
schemas = [join(schema_path, f) for f in listdir(schema_path) if isfile(join(schema_path, f))]
print(schemas)

mypath = 'task_folder/event/'
jsonfiles = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
print(jsonfiles)

for filename in jsonfiles:
	try:
		df = pd.read_json(filename)
		print(filename)
		print(df)
	except:
		print(filename)
		print('error')

for filename in jsonfiles:
	print(filename)
	with open(filename, 'r') as f:
		instance = json.load(f)
		with open(schemas[1], 'r') as f2:
			schema = json.load(f2)
			print(validate(instance=instance, schema=schema))
				