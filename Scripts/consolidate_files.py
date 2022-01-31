import csv
import re
import logging
from os.path import join
from os import listdir
# from config import INPUT_DIR, FILE_A, FILE_B, FILE_C, CSHARE_CUTOFF, OUTPUT

BIG_NUMBER = 5e6 # This is a large number to be used as a placeholder search rank.

'''
The following bit will produce a series of input prompts for the user to specify
a cutoff value, as well as the input files to be used in order. It also gives the
user the option to enter a name for the output file, which will otherwise be 
generated automatically by the script.
'''
print('Please enter an upper cutoff value for conversion shares.')
CSHARE_CUTOFF = int(input('The cutoff value should be entered as percentage points (e.g. enter 80 for 80%): '))

INPUT_DIR = 'Files'
INPUT_FILES = {}

print('The following input files have been found in the Files directory:')
for i, f in enumerate(listdir(INPUT_DIR)):
    INPUT_FILES[i] = f
    print(f'[{i}]\t{f}')

FILE_A = INPUT_FILES[int(input('Please type the number that corresponds to the FIRST input file above: '))]
FILE_B = INPUT_FILES[int(input('Please type the number that corresponds to the SECOND input file above: '))]
FILE_C = INPUT_FILES[int(input('Please type the number that corresponds to the THIRD input file above: '))]

print('The script will generate a filename automatically.')
output_fn = input('If you wish to specify a filename yourself please enter it here (with the file extension). Otherwise hit Enter to start the script: ')

# The following will store the lowercase equivalent of included search terms with apostrophes removed.
all_terms = []
# The following will store a list of unique titles related to included search terms.
all_titles = {}
#The two below will store the included and excluded search terms, respectively.
included_terms = {}
excluded_terms = {}

def to_number_or_zero(perc):
    '''
    Tries to convert a string that is supposed to represent a percentage value to a float.
    If the string has a typo returns zero.

    This was necessary as some percentage fields have non-numeric characters, which caused
    the script to crash.
    '''
    try:
        return float(perc[:perc.find('%')])
    except ValueError:
        return 0

class TermRecord():
    def __init__(self, search_term):
        self.search_term = search_term
        self.appearances = 1 # Number of files including the term
        self.file_c_columns = ['']*12 # Stores data from columns D-O of third file
        self.ranks = {
            FILE_A: BIG_NUMBER, #SFR for the first month
            FILE_B: BIG_NUMBER, #SFR for the first month
            FILE_C: BIG_NUMBER, #SFR for the first month
        }
        self.cshares = {
            FILE_A: None, # Sum of conversion shares for the first month
            FILE_B: None, # Sum of conversion shares for the second month
            FILE_C: None, # Sum of conversion shares for the third month
            
        }
        self.term_freq = None
        self.title_freq = None

    def add_file_c_columns(self, col_data):
        self.file_c_columns = col_data

    def calculate_trend(self):
        '''
        This method determines if the search term is trending up/down. 
        '''
        rank_diffs = [self.ranks[FILE_A] - self.ranks[FILE_B], self.ranks[FILE_B] -  self.ranks[FILE_C]]
        if rank_diffs[0] == rank_diffs[1] == 0: # The rank is the exact same in all three months
            return 'Stable'
        elif rank_diffs[0] >= 0 and rank_diffs[1] >= 0:
            return 'Trending Up'
        elif rank_diffs[0] <= 0 and rank_diffs[1] <= 0:
            return 'Trending Down'
        else: # The rank changes in opposite directions
            return 'Inconsistent'

    def calculate_avg_rank(self):
        '''
        This method first sets the rank to zero for files in which the search term could not be found,
        then calculates the average rank of the search term across three files.
        '''
        return sum([r if r < BIG_NUMBER else 0 for r in self.ranks.values()]) / self.appearances

    def calculate_avg_cshare(self):
        '''
        Method to calculate the average conversion share over three months.
        '''
        return sum([c if c is not None else 0 for c in self.cshares.values()]) / self.appearances

    def calculate_term_frequencies(self):
        '''
        Method to calculate the frequency of search term within all the included terms.
        Single quotes/ apostrophes are removed from search.
        '''
        self.term_freq = all_terms.count(self.search_term.replace("'",""))

    def calculate_title_frequencies(self):
        '''
        Method to calculate the frequency of search term in all titles associated with
        the included search terms in the last month.
        '''
        self.title_freq = all_titles.count(self.search_term.replace("'",""))

    def generate_output_row(self):
        '''
        Returns an output row with all the required data about the search term
        '''
        trend = self.calculate_trend()
        avg_rank = self.calculate_avg_rank()
        avg_cshare = self.calculate_avg_cshare()
        return [
            self.search_term,
            self.term_freq,
            self.title_freq,
            f'{avg_rank:.2f}',
            trend,
            self.appearances,
            f'{self.cshares[FILE_A]:.2f}%' if self.cshares[FILE_A] else '',
            f'{self.cshares[FILE_B]:.2f}%' if self.cshares[FILE_B] else '',
            f'{self.cshares[FILE_C]:.2f}%' if self.cshares[FILE_C] else '',
            f'{avg_cshare:.2f}%',
        ] + self.file_c_columns + [
            self.ranks[FILE_A],
            self.ranks[FILE_B],
            self.ranks[FILE_C],
        ]


def parse_file(filename): #, terms_list, titles_list):
    global all_terms
    global all_titles
    add_cols = filename == FILE_C # If it's the last file we're processing we'll add columns from this file)
    with open(join(INPUT_DIR, filename), 'r', encoding='utf-8') as infile:
        rdr = csv.reader(infile, delimiter=',')
        next(rdr)
        title_row = next(rdr)
        for row in rdr:
            # First determine if we need to exclude this term:
            term = row[1].strip().lower() # Store a lowercase version of the term to avoid mismatches due to case differences
            if len(term) < 2:
                continue # Skip one-character search terms.
            if term in excluded_terms: # We already added this term to exclude list while parsing previous files
                continue
            c_share_1 = row[6].strip()
            c_share_1 = to_number_or_zero(c_share_1)
            exclude = c_share_1 < 1. # Exclude if #1 conversion share is < 1%
            if not exclude:
                c_share_2 = row[10].strip()
                c_share_2 = to_number_or_zero(c_share_2)
                exclude = c_share_2 < 1. # Exclude if #2 conversion share is < 1%
                if not exclude:
                    c_share_3 = row[14].strip()
                    c_share_3 = to_number_or_zero(c_share_3)
                    total_c_share = c_share_1 + c_share_2 + c_share_3 # calculate the sum of conversion shares
                    exclude = total_c_share >= CSHARE_CUTOFF # exclude if sum of conversion shares is >= threshold we set.
            if exclude:
                if term in included_terms: # If we previously included this term remove it first.
                    included_terms.pop(term)
                excluded_terms[term] = None
                continue
            # We are including this term, so continue to process the row.
            rank =  int(row[2].replace(',','').strip()) 
            if term in included_terms:
                term_record = included_terms[term]
                term_record.appearances +=1
            else:
                term_record = TermRecord(term)
                included_terms[term] = term_record
            term_record.cshares[filename] = total_c_share
            term_record.ranks[filename] = rank
            # Add the search term to the lookup
            all_terms.append(term.replace("'", ""))
            # If it's the last month add columns D-O from this file to the output and store the titles for search term lookup.
            if add_cols:
                term_record.add_file_c_columns(row[3:])
                titles = (
                    row[4].strip().lower(), 
                    row[8].strip().lower(), 
                    row[12].strip().lower()
                )
                for t in titles:
                    if t not in all_titles:
                        all_titles[t] = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s') 
    logger = logging.getLogger(name='loglog')
    logger.info('Beginning to parse input files.')
    for fn in [FILE_A, FILE_B, FILE_C]:
        parse_file(fn)
        logger.info(f'Finished parsing {fn}.')
    logger.info(f'{len(included_terms)} out of {len(excluded_terms)+len(included_terms)} terms will be written to the output file.')
    # Join the search terms and titles into strings for better search performance.
    all_terms = '. '.join(all_terms)
    all_titles = '. '.join(all_titles.keys())
    if output_fn == '':
        # Generate a filename if it's not specified by user, using the timestamp of this moment 
        from datetime import datetime as dt
        ts = dt.now().strftime('%Y-%m-%d-%I%M%S%p')
        output_fn = f'FinalFile_{ts}.csv'
    elif output_fn[-4:].lower() not in ['.csv', '.txt']:
        # If the filename entered by the user doesn't include a valid file extension add it.
        output_fn += '.csv'
    logger.info(f'Calculating term and title frequencies and writing them to output file {output_fn}')
    with open(output_fn, 'w', encoding='utf-8') as outputfile:
        writer = csv.writer(outputfile, delimiter=',')
        writer.writerow([
            'Search Term',
            'Term Frequency',
            'Title Frequency',
            'Average Search Ranking',
            'Trend',
            'No. of Appearances',
            'Month 1 Conversion Share',
            'Month 2 Conversion Share',
            'Month 3 Conversion Share',
            'Average Conversion Share',
            '#1 Clicked ASIN (From Month 3)',
            '#1 Product Title (From Month 3)',
            '#1 Click Share (From Month 3)',
            '#1 Conversion Share (From Month 3)',
            '#2 Clicked ASIN (From Month 3)',
            '#2 Product Title (From Month 3)',
            '#2 Click Share (From Month 3)',
            '#2 Conversion Share (From Month 3)',
            '#3 Clicked ASIN (From Month 3)',
            '#3 Product Title (From Month 3)',
            '#3 Click Share (From Month 3)',
            '#3 Conversion Share (From Month 3)',
            'Month 1 Search Rank',
            'Month 2 Search Rank',
            'Month 3 Search Rank',
        ])
        for tf in included_terms.values():
            tf.calculate_term_frequencies()
            tf.calculate_title_frequencies()
            writer.writerow(tf.generate_output_row())
    logger.info('DONE.')
