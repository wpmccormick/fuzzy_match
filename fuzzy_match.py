#!/usr/bin/env python3
# pylint: disable=invalid-name
from __future__ import print_function
from sys import exit
from thefuzz import fuzz
import argparse
import json
import csv

class JsonConfigKeyError(KeyError):
	"""Custom exception for missing keys in the JSON config file."""
	pass

class CsvColumnKeyError(KeyError):
	"""Custom exception for missing keys in the CSV file."""
	pass

class Filter:
	"""Class to hold a filter."""
	def __init__(self, filter_str):
		"""Initialize the filter."""
		#load the filer into a dictionary
		self.filter_dict = {}

		try:
			for f in filter_str.split("+"):
				#split the filter into a key and value
				[key, values] = f.split("=")

				#check if the key is already in the dictionary
				if key in self.filter_dict.keys():
					self.filter_dict[key.strip()].append([value.strip() for value in values.split(",")])
				else:
					self.filter_dict[key.strip()] = [value.strip() for value in values.split(",")]
		except ValueError as e:
			raise ValueError(e)
		except Exception as e:
			raise Exception(e)

	def match(self, csv_row):
		"""Check if the CSV row passes the filter."""
		match = 0

		#check if the row matches the filter
		for key in self.filter_dict.keys():
			if key in csv_row.keys():
				for value in self.filter_dict[key]:
					if csv_row[key] == value:
						match+=1
			else:
				raise CsvColumnKeyError("Filter key [%s] is not a valid column header." % key)
		
		return match == len(self.filter_dict.keys())

def arg_parse():
	# Create an argument parser
	parser = argparse.ArgumentParser(description="Fuzzy match two CSV files.")

	# Specify the CSV and XML files as a command line argument
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-v', '--verbose',	action='store_true', help="Print more information to the console")

	parser.add_argument(
		'-t', 
		'--test', 
		required=True, 
		help="Path to the test input CSV file"
	)

	parser.add_argument(
		'-r', 
		'--relation', 
		required=True, 
		help="Path to the relation input CSV file"
	)
	
	parser.add_argument(
		'-s', 
		'--score', 
		required=True, 
		help="Minium score to be considered a match"
	)
	
	# parser.add_argument(
	# 	'-o',
	# 	'--outfile', 
	# 	required=True,
	# 	help="Output file name."
	# )

	parser.add_argument(
		'-c', 
		'--config', 
		default="config.json",
		help="Path to configuration file. Default: config.json"
	)
	
	parser.add_argument(
		'-e',
		'--encoding',
		default='utf-8',
		help='Select a file output encoding: [utf-8, utf-16, utf-32, ascii, latin1, cp1252, etc.]; default utf-8'
	)

	# Parse the command line arguments
	args = parser.parse_args()

	return args

def create_filter(filter_str):

	try:
		filter = Filter(filter_str) if filter_str else None
	except ValueError as e:
		raise ValueError("Filter format not correct: [%s]" % e)
	except Exception as e:
		raise Exception("Exception handling filter: [%s]" % e)

	return filter

def calc_scores(test, reference):
	"""
	Score the test string against the reference string using the average of the
	Levenshtein and partial ratio, set and sort scores.
	"""
	scores = {}

	# Calculate the Levenshtein ratio
	scores["lev_ratio"] = fuzz.ratio(test, reference)

	# Calculate the partial ratio
	scores["partial_ratio"] = fuzz.partial_ratio(test, reference)

	# Calculate the set ratio
	scores["set_ratio"] = fuzz.token_set_ratio(test, reference)

	# Calculate the sort ratio
	scores["sort_ratio"] = fuzz.partial_token_sort_ratio(test, reference)

	return scores


def replace_strings(original_string, replacements_dict):
	"""Replace strings in the original string with the replacement strings."""

	for key in replacements_dict:
		for value in replacements_dict[key]:
			original_string = original_string.replace(value, key)

	return original_string

def main():

	try:
		args = arg_parse()

		test_file_name = args.test
		relation_file_name = args.relation
		#out_file_name = args.outfile
		config_file_name = args.config
		min_score = int(args.score)

		#open the json file and read the logic config
		with open(config_file_name, 'r',encoding=args.encoding) as config_file:
			config = json.load(config_file)

		try:
			test_filter = create_filter(config["source"]["filter"])
			test_text = config["source"]["text"]
			relation_filter = create_filter(config["relation"]["filter"])
			relation_text = config["relation"]["text"]
			relation_ignore = config["relation"]["ignore"]
			relation_alias = config["relation"]["alias"]

			#output_columns = config["output"].keys()
		except KeyError as e:
			raise JsonConfigKeyError("Key [%s] is missing from the JSON config file." % e)
		except Exception as e:
			raise Exception("Exception handling filter: [%s]" % e)

		# if out_file_name is None:
		# 	raise Exception("Output file cannot be none")

		# # ask to overwrite the output file exists
		# if os.path.isfile(out_file_name) and not args.test:
		# 	raise FileExistsError("Output file [%s] already exists." % out_file_name) # pylint: disable=undefined-variable
		
		# Read the source test file
		with open(test_file_name, 'r', encoding=args.encoding) as test_file:
			test_csv_reader = csv.DictReader(test_file)
			test_data = list(test_csv_reader)

		# Read the relation file
		with open(relation_file_name, 'r', encoding=args.encoding) as relation_file:
			rel_csv_reader = csv.DictReader(relation_file)
			relation_data = list(rel_csv_reader)

		print("Fuzzy matching started ingesting file [%s] looking for matches in [%s]." % (test_file_name, relation_file_name))

		for test_index, test_row in enumerate(test_data):
			test_string = ""

			if test_filter and not test_filter.match(test_row):
				continue
			
			for col in test_text:
				test_string += test_row[col] + " "
			
			test_string = test_string.strip()
			
			# replace alias
			test_string_alias = replace_strings(test_string, relation_alias)

			max_score = {}
			max_score["score"] = 0

			for rel_index, rel_row in enumerate(relation_data):
				rel_string = ""

				if relation_filter and not relation_filter.match(rel_row):
					continue

				for col in relation_text:
					rel_string += rel_row[col] + " "

				rel_string = rel_string.strip()
					
				if any(str in rel_string for str in relation_ignore):
					continue
					
				scores = calc_scores(test_string_alias, rel_string)

				for method in scores:
					if scores[method] >= min_score and scores[method] > max_score["score"]:
						max_score["match_string"] = rel_string
						max_score["score"] = scores[method]
						max_score["method"] = method
			
			if max_score["score"] >= min_score:
				print(f'{test_string},{max_score["match_string"]},{max_score["score"]},{max_score["method"]}')


	except Exception as e:
		import traceback
		print("Fuzzy match failed: [%s]" % e)
		if args.verbose:
			traceback.print_exc()

		exit(1)

if __name__ == "__main__":
	main()
