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
	
#program to read the the causality tree csv file's first 3 columns and create a dictionary of alias
args = parser.parse_args()

# open the csv file
with open(args.alias, 'r') as alias_file:
	try:
		alias_csv_reader = csv.DictReader(alias_file)
		alias_data = list(alias_csv_reader)

		print(alias_data)

		alias_dict = {}
		for alias in alias_data:
			alias_dict[alias[0]] = alias[1]
	except csv.Error as e:
		raise Exception(f"Error reading CSV file '{alias_file_name}': {e}")

# read the first 3 columns
# create a dictionary of alias
#