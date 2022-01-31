INPUT_DIR = 'Files' #This is the directory under which input files are stored.

'''
Change the filenames below to match the monthly result files before each time
you run the script. Following the convention in the slide deck, FILE_A is the
oldest file and FILE_C is the newest file. Make sure to include the file 
extension and surround the filename in single or double quotes.
'''
FILE_A = 'Amazon Search Terms Oct 2021 CSV.csv'
FILE_B = 'Amazon Search Terms Nov 2021 CSV.csv'
FILE_C = 'Amazon Search Terms Dec 2021 CSV.csv'

'''
If you wish, you may specify an output filename below. If left blank, the filename 
will be automatically generated by the script.
'''
OUTPUT = ''

'''
The variable below represents a percentage value. Search terms with an aggregate
conversion rate above this percentage will be excluded from the final file.
Adjust this number as needed. 
The number represents percentage points; i.e. 80 corresponts to 80%, 90 to 90%.
'''
CSHARE_CUTOFF = 40
