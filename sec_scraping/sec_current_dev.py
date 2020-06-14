import collections
import re
from pprint import pprint
from re import Pattern
from sec_scraping.sec_scraping_unit_tests import all_in_one_dict_gilead
import sec_scraping.scraping_regexes as fin_reg

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

master_dict = {}
pprint(flatten(all_in_one_dict_gilead))

# TODO to generalize further, each pattern is actually the name of the key
# case insensitive,
# starts with either title or name of parent category
# excludes words from other entries in category
# exclude : , etc. with any characters in between each word


for scraped_name, scraped_value in flatten(all_in_one_dict_gilead).items():
    for normalized_category, pattern in flatten(fin_reg.financial_entries_regex_dict).items():

        if isinstance(pattern, Pattern):
            pattern_match = re.search(pattern, scraped_name)
            if pattern_match:

                # this takes care of having two entries for marketable securities, accounts receivables as in Goldman Sachs
                if normalized_category in master_dict.keys():
                    master_dict[normalized_category] += scraped_value
                else:
                    master_dict[normalized_category] = scraped_value

                if 'Cash Flow Statement' in normalized_category: # TODO beware _ and : normalize!
                    master_dict[normalized_category+'_'+pattern_match.string.split(':')[-1]] = scraped_value

pprint(master_dict)

balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
pprint(balance_sheet)