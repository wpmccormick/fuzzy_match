# fuzzy_match
Uses Fuzzy String Matching to make connections between 2 lists of strings. Accepts input from a *test* CSV file and makes comparisons with a *relation* input CSV file based on parameters set in a configuration file.
## command line options
  -t TEST, --test TEST  				Path to the test input CSV file
  -r RELATION, --relation RELATION		Path to the relation input CSV file
  -s SCORE, --score SCORE				Minium score to be considered a match
  -c CONFIG, --config CONFIG			Path to configuration file. Default: config.json
  -e ENCODING, --encoding ENCODING		Select a file output encoding: [utf-8, utf-16, utf-32, ascii, latin1, cp1252, etc.]; default utf-8
  -h, --help            				show this help message and exit
  --version             				show program's version number and exit
  -v, --verbose         				Print more information to the console

## configurtion
Unless otherwsie specified with the *config* option the *config.json*  file is used with the following parameters:
```
{
	"source": {
		"filter": "Fault=Yes",
		"text": ["Name"]
	},
	"relation": {
		"filter": "model=Arcil 11+C1Name=Packer",
		"text": ["C2Name","C3Name"],
		"ignore": ["EXPLAIN","NC REQUIRED"],
		"alias": {
			"Extractor": ["Box filler","Pick&Place"],
			"Feeder": ["Tray Former"],
			"Closing": ["Case Sealer","Box sealer"],
			"Outfeed": ["Stacker","Elevator"]
		}
	}
}
```
### source
Defines which columns to join together for testing against relations using the list of *text*  column names. Use *filter* to consider rows that match some condition. Multiple conditions can be specified (OR with ,; AND with +) . 

### relation
Defines which columns to join together for relations that are tested against using the list of *text*  column names. Use *filter* to consider rows that match some condition. Multiple conditions can be specified (OR with ,; AND with +). Use *ignore* to skip any text that contains words in the list. Use *alias* to replace test words from the source before scoring to improve scores.

## output
The output is a CSV format with the following columns:
```
<Original source/test text>,<matched text from relations>,<score>,<fuzzy method with highest score>
```
## references
[Fuzzy String Matching in Python Tutorial](https://www.datacamp.com/tutorial/fuzzy-string-python)
[thefuzz on gitub](https://github.com/seatgeek/thefuzz)
[Senzing - $$$](https://senzing.com/)

