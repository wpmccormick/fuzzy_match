#!/usr/bin/env python3
import csv
import yaml
import argparse

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

args = parser.parse_args()

#program to read the the causality tree csv file's first 3 columns and create a dictionary of alias

# open the csv file
with open(args.alias, 'r') as alias_file:
	try:
		alias_csv_reader = csv.DictReader(alias_file)
		alias_data = list(alias_csv_reader)

		#print(alias_data)

		alias_dict = {}
		for alias in alias_data:
			if alias["model"] not in alias_dict.keys():
				alias_dict[alias["model"]] = []
				alias_dict[alias["model"]].append({alias["C1Name"]: [{alias["C2Name"]:["alias1","alias2"]}]})
			else:

				C2Name = next((a for a in alias_dict[alias["model"]] if alias["C1Name"] in a), None)
				if C2Name is None:
					alias_dict[alias["model"]].append({alias["C1Name"]: [{alias["C2Name"]:["alias1","alias2"]}]})
				else:
					if not any(alias["C2Name"] in a for a in C2Name[alias["C1Name"]]):
						C2Name[alias["C1Name"]].append({alias["C2Name"]:["alias1","alias2"]})
					else:
						pass

				# if not any(alias["C1Name"] in a for a in alias_dict[alias["model"]]):
				# else:
				# 	C2Name = next((a for a in alias_dict[alias["model"]] if alias["C1Name"] in a), None)
					
					# if not any(alias["C2Name"] in a for a in C2Name[alias["C1Name"]]):
					# 	C2Name[alias["C1Name"]].append({alias["C2Name"]:["alias1","alias2"]})
					# else:
					# 	pass
			

		with open(args.output, 'w') as yaml_file:
			yaml.dump(alias_dict, yaml_file, default_flow_style=False)
			
		
		exit()
		# 		alias_dict[alias["model"]] = [{alias["C1Name"]}].append(alias["C2Name"])
		# 	else:
		# 		if alias["C1Name"] not in alias_dict[alias["model"]]:
		# 			alias_dict[alias["model"]].append(alias["C1Name"])

		# print(alias_dict)
					
	except csv.Error as e:
		raise Exception(f"Error reading CSV file '{alias_file}': {e}")

# read the first 3 columns
# create a dictionary of alias
#