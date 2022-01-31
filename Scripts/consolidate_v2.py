import csv
import re
import logging
from os.path import join
from config import INPUT_DIR, FILE_A, FILE_B, FILE_C, CSHARE_CUTOFF, OUTPUT

BIG_NUMBER = 5e6 # This is a large number to be used as a placeholder search rank.

# The following will store all search terms in files
all_terms = {
    FILE_A : [],
    FILE_B : [],
    FILE_C : []
}
# The following will store all titles in files
# all_titles = {
#     FILE_A : [], 
#     FILE_B : [], 
#     FILE_C : [],
# }
all_titles = {
    FILE_A : {}, 
    FILE_B : {}, 
    FILE_C : {},
}
#The two below will store the included and excluded search terms, respectively.
included_terms = {}
excluded_terms = {}

class TermRecord():
    def __init__(self, search_term):
        self.search_term = search_term
        self.appearances = 1 # Number of files including the term
        self.file_c_columns = ['NA']*12 # Stores data from columns D-O of third file
        self.ranks = {
            FILE_A: BIG_NUMBER, #SFR for the first month
            FILE_B: BIG_NUMBER, #SFR for the first month
            FILE_C: BIG_NUMBER, #SFR for the first month
        }
        self.shares = {
            FILE_A: None, # Sum of conversion shares for the first month
            FILE_B: None, # Sum of conversion shares for the second month
            FILE_C: None, # Sum of conversion shares for the third month
            
        }
        self.term_freqs = {
            FILE_A: None, # Number of times the search term appears in search terms in first file
            FILE_B: None, # Number of times the search term appears in search terms in second file
            FILE_C: None, # Number of times the search term appears in search terms in third file
        }
        self.title_freqs = {
            FILE_A: None, # Number of times the search term appears in titles in first file
            FILE_B: None, # Number of times the search term appears in titles in second file
            FILE_C: None, # Number of times the search term appears in titles in third file
        } 

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
        sum_ranks = 0
        for k, v in self.ranks.items():
            if v == BIG_NUMBER:
                self.ranks[k] = 0
            else:
                sum_ranks += v
        return sum_ranks / self.appearances

    def calculate_term_frequencies(self):
        '''
        Method to calculate the frequency of search term in all terms for each month.
        Only whole word matches are counted.
        '''
        self.term_freqs[FILE_A] = all_terms[FILE_A].count(self.search_term)
        self.term_freqs[FILE_B] = all_terms[FILE_B].count(self.search_term)
        self.term_freqs[FILE_C] = all_terms[FILE_C].count(self.search_term)

        # self.term_freqs[FILE_A] = len(re.findall(r'\b' + self.search_term + r'\b', all_terms[FILE_A]))
        # self.term_freqs[FILE_B] = len(re.findall(r'\b' + self.search_term + r'\b', all_terms[FILE_B]))
        # self.term_freqs[FILE_C] = len(re.findall(r'\b' + self.search_term + r'\b', all_terms[FILE_C]))

        # self.term_freqs[FILE_A] = len([t for t in all_terms[FILE_A] if self.search_term in t])
        # self.term_freqs[FILE_B] = len([t for t in all_terms[FILE_B] if self.search_term in t])
        # self.term_freqs[FILE_C] = len([t for t in all_terms[FILE_C] if self.search_term in t])

    def calculate_title_frequencies(self):
        '''
        Method to calculate the frequency of search term in all titles for each month.
        Only whole word matches are counted.
        '''
        self.title_freqs[FILE_A] = all_titles[FILE_A].count(self.search_term)
        self.title_freqs[FILE_B] = all_titles[FILE_B].count(self.search_term)
        self.title_freqs[FILE_C] = all_titles[FILE_C].count(self.search_term)

        # self.title_freqs[FILE_A] = len(re.findall(r'\b' + self.search_term + r'\b', all_titles[FILE_A]))
        # self.title_freqs[FILE_B] = len(re.findall(r'\b' + self.search_term + r'\b', all_titles[FILE_B]))
        # self.title_freqs[FILE_C] = len(re.findall(r'\b' + self.search_term + r'\b', all_titles[FILE_C]))
        # self.title_freqs[FILE_A] = len([t for t in all_titles[FILE_A].keys() if self.search_term  in t])
        # self.title_freqs[FILE_B] = len([t for t in all_titles[FILE_B].keys() if self.search_term  in t])
        # self.title_freqs[FILE_C] = len([t for t in all_titles[FILE_C].keys() if self.search_term  in t])

    def generate_output_row(self):
        '''
        Returns an output row with all the required data about the search term
        '''
        trend = self.calculate_trend()
        avg_rank = self.calculate_avg_rank()
        return [
            self.search_term,
            self.term_freqs[FILE_A],
            self.term_freqs[FILE_B],
            self.term_freqs[FILE_C],
            self.title_freqs[FILE_A],
            self.title_freqs[FILE_B],
            self.title_freqs[FILE_C],
            f'{avg_rank:.2f}',
            trend,
            self.appearances,
            f'{self.shares[FILE_A]:.2f}%' if self.shares[FILE_A] else '',
            f'{self.shares[FILE_B]:.2f}%' if self.shares[FILE_B] else '',
            f'{self.shares[FILE_C]:.2f}%' if self.shares[FILE_C] else '',
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
            term = row[1].strip().lower() # Store a lowercase version of the term to avoid mismatches due to case differences
            # terms_list.append(term)
            # all_terms[filename] = ' '.join([all_terms[filename], term + '.'])
            all_terms[filename].append(term)
            # all_titles[filename] = ' '.join([
            #     all_titles[filename], 
            #     row[4].strip().lower() + '.', 
            #     row[8].strip().lower() + '.', 
            #     row[12].strip().lower() + '.'
            #     ]
            # )
            # all_titles[filename].append(' '.join(
            #     [
            #         row[4].strip().lower() + '.', 
            #         row[8].strip().lower() + '.', 
            #         row[12].strip().lower() + '.'
            #     ]
            # )
            # )
            titles = (
                row[4].strip().lower(), 
                row[8].strip().lower(), 
                row[12].strip().lower()
            )
            for t in titles:
                if t not in all_titles[filename]:
                    all_titles[filename][t] = None
            # First determine if we need to exclude this term:
            exclude = term in excluded_terms # We already added this term to exclude list while parsing previous files
            if exclude:
                continue
            c_share_1 = row[6].strip()
            try:
                c_share_1 = float(c_share_1[:c_share_1.find('%')])
                exclude = c_share_1 < 1. # Exclude if #1 conversion share is < 1%
            except ValueError:
                # logger.warning(f'Unable to process conversion share #1: {c_share_1}')
                exclude = True
            if not exclude:
                c_share_2 = row[10].strip()
                c_share_2 = float(c_share_2[:c_share_2.find('%')])
                exclude = c_share_2 < 1. # Exclude if #2 conversion share is < 1%
                if not exclude:
                    c_share_3 = row[14].strip()
                    c_share_3 = float(c_share_3[:c_share_3.find('%')])
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
            term_record.shares[filename] = total_c_share
            term_record.ranks[filename] = rank
            if add_cols: # If it's the last month add columns D-O from this file to the output.
                term_record.add_file_c_columns(row[3:])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s') 
    logger = logging.getLogger(name='loglog')
    logger.info('Beginning to parse input files.')
    for fn in [FILE_A, FILE_B, FILE_C]:
        parse_file(fn)
        logger.info(f'Finished parsing {fn}.')
    logger.info(f'{len(included_terms)} out of {len(excluded_terms)+len(included_terms)} terms will be written to otput file.')
    # Join the search terms and titles into strings for better search performance.
    for k, v in all_terms.items():
        all_terms[k] = '. '.join(v)
    for k, v in all_titles.items():
        all_titles[k] = '. '.join(v.keys())
    if OUTPUT == '':
        # Generate a filename if it's not specified, using the timestamp of this moment 
        from datetime import datetime as dt
        ts = dt.now().strftime('%Y-%m-%d-%I%M%S%p')
        OUTPUT = f'FinalFile_{ts}.csv'
    logger.info('Calculating term and title frequencies and creating output file.')
    with open(OUTPUT, 'w', encoding='utf-8') as outputfile:
        writer = csv.writer(outputfile, delimiter=',')
        writer.writerow([
            'Search Term',
            'Month 1 Term Frequency',
            'Month 2 Term Frequency',
            'Month 3 Term Frequency',
            'Month 1 Title Frequency',
            'Month 2 Title Frequency',
            'Month 3 Title Frequency',
            'Average Search Ranking',
            'Trend',
            'No. of Appearances',
            'Month 1 Conversion Share',
            'Month 2 Conversion Share',
            'Month 3 Conversion Share',
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
    
            
                
'''
TODO:
Need to tell Gerry:
    -I've included an extra status for trends to cover the case when the rank is the exact same across all files.
    -While searching for occurrences of a term in other fields we might look for whole word matches. i.e. if we're 
     looking for "elf" in other fields "Self will not yield a match. This does have two drawbacks: 1: It is A LOT slower.
     2: We will miss plural/singular matches; e.g. 'christmas lights' won't yield a match for 'light'
    -I discard duplicate titles while looking up search terms in title fields. That is, if a title shows up for multiple products
     we look for search terms in this title only once per month.
    -It's not entirely clear in process #7 whether we should look for matches of the search term in the final file only or in all
     terms/titles in each file. i.e. do we look for a search term within all other search terms and titles in Oct, Nov and Dec files
     separately (amond all terms/titles regardless of whether we include them in the final file) or do we need to perform search only
     once, among what we have in the final output file.
    -Another point that isn't entirely clear is whether we exclude terms that have a combined conversion share above the threshold
     within any month or based on the SUM of combined thresholds in all months (referring to Process #5). 
     If we go by the combined share per month, we have the following numbers of terms included in the final file (out of 1335804 terms in total)
     with different thresholds:
        90%: 766,950
        80%: 614,426
        70%: 462,879
        60%: 314,522
        50%: 186,338
        40%:  96,532
        30%:  36,445
        20%:   7,508
    -I suggest we remove apostrophes from the term and title fields so that "men's slippers" and "mens slippers" are not treated
     as different search terms  
    -There are single letter search terms, which look a lot like accidental clicks to me and I doubt that there's any
     useful information in these. I currently didn't discard them but would be happy to do so if he'd agree.
'''


            
