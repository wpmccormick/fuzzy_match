#!/usr/bin/env python3
# pylint: disable=invalid-name
from __future__ import print_function
from sys import exit
from thefuzz import process
import argparse
import json
import csv
import os

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
	parser = argparse.ArgumentParser(description="Fault Mapper")

	# Specify the CSV and XML files as a command line argument
	parser.add_argument('--version', action='version', version='%(prog)s 0.1')
	parser.add_argument('-v', '--verbose',	action='store_true', help="Print more information to the console")

	parser.add_argument(
		'--csv', 
		required=True, 
		help="Path to the input CSV file"
	)

	parser.add_argument(
		'--tree', 
		default="tree.json",
		help="Causality Tree Default: tree.json"
	)
	
	parser.add_argument(
		'--alias', 
		default="alias.json",
		help="Causality Tree Alias Specs Default: alias.json"
	)
	
	parser.add_argument(
		'--score', 
		default="50",
		help="Causality match score Default: 50"
	)
	
	parser.add_argument(
		'-e',
		'--encoding',
		default='utf-8',
		help='Select a file output encoding: [utf-8, utf-16, utf-32, ascii, latin1, cp1252, etc.]; default utf-8'
	)

	parser.add_argument(
		'-z',
		'--fuzz',
		default='Text',
		help='Select a fuzz type: [Text, Ratio, PartialRatio, TokenSortRatio, TokenSetRatio]; default Text'
	)
		
	parser.add_argument(
		'-c',
		'--column',
		default='Text',
		help='Select a csv column to fuzz on. Default Text'
	)
		
	parser.add_argument(
		'-f',
		'--filter', 
		help="Choose columns and spec to filter out rows that do not match the spec: [column=value,...+column=value,...]"
	)

	parser.add_argument(
		'-t',
		'--test', 
		action='store_const', 
		const=True,
		help="Don't generate output file; just test the filter."
	)

	parser.add_argument(
		'-o',
		'--outfile', 
		required=True,
		help="Output file name."
	)

	# Parse the command line arguments
	args = parser.parse_args()

	return args

def create_filter(args):

	filter_str = args.filter

	try:
		filter = Filter(filter_str) if filter_str else None
	except ValueError as e:
		raise ValueError("Filter format not correct: [%s]" % e)
	except Exception as e:
		raise Exception("Exception handling filter: [%s]" % e)

	if filter:		
		print("Filtering rows based on the following criteria:") 		
		for key in filter.filter_dict:
			print("  %s=%s" % (key, filter.filter_dict[key]))

	return filter

def classify(input_string, tree, score=0):
    # Use process.extract to get a list of matches and their similarity scores
	
	l2_score = 0
	l2_match = ''

	l1_matches = process.extract(input_string, tree.keys(), limit=3)

	# Extract the top match and its similarity score
	l1_match, l1_score = l1_matches[0]

	if l1_score > int(score):
		if len(tree[l1_match]) > 0:
			l2_matches = process.extract(input_string, tree[l1_match], limit=3)
			l2_match, l2_score = l2_matches[0]
		
		if l2_score > int(score):
			return l1_score, l1_match, l2_score, l2_match
		else:
			return l1_score, l1_match, 0, ''
	else:
		return 0, '', 0, ''

def main():

	try:
		args = arg_parse()

		csv_file_name = args.csv
		out_file_name = args.outfile
		tree_file_name = args.tree


		if out_file_name is None:
			raise Exception("Output file cannot be none for PLC format [%s]" % args.plc)

		filter = create_filter(args)

		# ask to overwrite if l5x file exists
		if os.path.isfile(out_file_name) and not args.test:
			raise FileExistsError("Output file [%s] already exists." % out_file_name) # pylint: disable=undefined-variable
		
		# Read the CSV file
		with open(csv_file_name, 'r', encoding=args.encoding) as csv_file:
			csv_reader = csv.DictReader(csv_file)
			data = list(csv_reader)

		#open the json file and read the logic config
		with open(tree_file_name, 'r',encoding=args.encoding) as json_file:
			tree = json.load(json_file)

		print("Classification started ingesting file [%s] with tree [%s] to create output file [%s]." % (csv_file_name, tree_file_name, out_file_name))

		match_count = 0

		# Convert CSV data to rungs
		for index, row in enumerate(data):

			row_num = index + 1

			try:
				if filter and not filter.match(row):
					continue

				match_count += 1


				if args.test:
					print(input_test)
					continue
			

				input_test = row[args.column]

				l1_score, l1_match, l2_score, l2_match = classify(input_test, tree, args.score)

				print(f"[Score: {l1_score}/{l2_score}][Causality: [{l1_match}/{l2_match}]] {input_test} ")


			except CsvColumnKeyError as e:
				print("Fault mapping failed on row [%d]: [%s]" % (row_num, e))
				raise e
			except Exception as e:
				print("Fault mapping failed on row [%d]: [%s]" % (row_num, e))
				raise e
			
	except Exception as e:
		import traceback
		print("Fault Mapping failed: [%s]" % e)
		if args.verbose:
			traceback.print_exc()

		exit(1)

if __name__ == "__main__":
	main()
