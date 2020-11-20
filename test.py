import os
import json
import pandas as pd
import jsonschema


jsonpath = 'task_folder/event/'
schemapath = 'task_folder/schema/'
jsonfiles = [os.path.join(jsonpath, f) for f in os.listdir(jsonpath)]
schemafiles = [os.path.join(schemapath, f) for f in os.listdir(schemapath)]


"""Можно было бы сделать по валидатору для каждой схемы
и прогонять каждый файл по четырем валидаторам,
а потом смотреть, какой схеме он больше соответствует.
Но для четырех схем проще сделать следующим образом.
"""
schemas = dict()
for filename in schemafiles:
	with open(filename, 'r') as f:
		schema = json.load(f)
		if 'activity_name' in schema['required']:
			schemas['workout'] = schema
		elif 'cmarkers' in schema['required']:
			schemas['cmarker'] = schema
		elif 'labels' in schema['required']:
			schemas['labels'] = schema
		else:
			schemas['sleep'] = schema


def choice_schema(data_keys: list) -> list:
	if 'labels' in data_keys:
		return schemas['labels']
	elif 'cmarkers' in data_keys:
		return schemas['cmarker']
	elif 'activity_name' in data_keys:
		return schemas['workout']
	else:
		return schemas['sleep']

def highlight(row):
	if row.Result == 'ok':
		return ['background-color: green'] * 4
	elif row.Result == 'no data':
		return ['background-color: red'] * 4
	else:
		return ['background-color: white'] * 4

def convert_error(error):
	if 'is a required property' in error.message:
		return "Пропущено обязательное поле"
	elif 'is not of type' in error.message:
		value = error.message.split(' ')[-1]
		return "Значение не соответствует типу {}".format(value)
	else:
		return error.message

def main():
	result = list()
	for j in jsonfiles:
		one = dict()
		with open(j, 'r') as f:
			data = json.load(f)
			try:
				schema = choice_schema(data['data'].keys())
				v = jsonschema.Draft3Validator(schema)
				errors = v.iter_errors(data['data'])
				for error in errors:
					message = convert_error(error)
					one = {'File': j, 'Result': 'error', 'Field': error.path[0], 'Message': message}
					result.append(one)
				if not one:
					one = {'File': j, 'Result': 'ok', 'Field': 'ok', 'Message': "ok"}
					result.append(one)	
		
			except KeyError as e:
				one = {'File': j, 'Result': 'no data', 'Field': 'all', 'Message': 'В файле нет данных'}
				result.append(one)
			except AttributeError as e:
				one = {'File': j, 'Result': 'no data', 'Field': 'data', 'Message': 'В файле недостаточно данных'}
				result.append(one)
			except TypeError as e:
				one = {'File': j, 'Result': 'no data', 'Field': 'all', 'Message': 'Файл пустой'}
				result.append(one)

	df = pd.DataFrame.from_records(result)
	print(df)
	html = df.style.apply(highlight, axis=1).set_caption('<h1>Валидация json</h1>').set_table_attributes(
					'border="1" class="dataframe table table-hover table-bordered"').render()

	with open('test.html', 'w') as f:
		f.write(html)

if __name__ == "__main__":
	main()