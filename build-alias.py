#!/usr/bin/env python3
#program to read the the causality tree csv file's first 3 columns and create a dictionary of alias
import csv
import yaml
import argparse
import os

parser = argparse.ArgumentParser(description="Build alias files.")

parser.add_argument(
	'-a', 
	'--alias', 
	help="Path to source/relation alias file"
)

parser.add_argument(
	'-o', 
	'--output', 
	help="Path to output file"
)

parser.add_argument(
	'-m', 
	'--model', 
	help="Restrict to a specific model"
)

parser.add_argument(
	'-c1', 
	'--c1name', 
	help="Restrict to a specific c1name"
)

args = parser.parse_args()

out_file_name =  args.output

# ask to overwrite the output file exists
if out_file_name is not None and os.path.isfile(out_file_name):
	raise FileExistsError("Output file [%s] already exists." % out_file_name) # pylint: disable=undefined-variable

filter_model = args.model
filter_c1name = args.c1name

# open the csv file
with open(args.alias, 'r') as alias_file:
	try:
		alias_csv_reader = csv.DictReader(alias_file)
		alias_data = list(alias_csv_reader)

		#print(alias_data)

		alias_dict = {}
		for alias in alias_data:
			model = alias["model"]
			c1name = alias["C1Name"]
			c2name = alias["C2Name"]

			if filter_model is not None and filter_model != model:
				continue

			if filter_c1name is not None and filter_c1name != c1name:
				continue

			# add new top model if not exist
			if model not in alias_dict.keys():
				alias_dict[model] = []
				alias_dict[model].append({c1name: [{c2name:['alias1','alias2']}]})
			
			else:
				# get the list of c1Names if they exist
				C2Names = next((a for a in alias_dict[model] if c1name in a), None)

				# if c1Name does not exist, add it
				if C2Names is None:
					alias_dict[model].append({c1name: [{c2name:['alias1','alias2']}]})

				# if c1Name exists, check if c2Name exists
				else:

					# if c2Name does not exist, add it
					if not any(c2name in a for a in C2Names[c1name]):
						C2Names[c1name].append({c2name:['alias1','alias2']})
					
					else:
						pass

		# check if the alias_dict is empty
		if not alias_dict:
			raise Exception(f'Nothing found for model {filter_model} and c1Name {filter_c1name}')

		with open(args.output, 'w') as yaml_file:
			yaml.dump(alias_dict, yaml_file, default_flow_style=False)
			
		
	except csv.Error as e:
		print(f"Error reading CSV file '{alias_file}': {e}")
	except Exception as e:
		print(e)