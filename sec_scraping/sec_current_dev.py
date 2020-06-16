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
# pprint(flatten(all_in_one_dict_gilead))

# TODO to generalize further, each pattern is actually the name of the key
# case insensitive,
# starts with either title or name of parent category
# excludes words from other entries in category
# exclude : , etc. with any characters in between each word




for scraped_name, scraped_value in flatten(all_in_one_dict_gilead).items():
    found_match = False
    for normalized_category, pattern in flatten(fin_reg.financial_entries_regex_dict).items():
        if isinstance(pattern, Pattern):
            pattern_match = re.search(pattern, scraped_name)
            # first we want to give priority to the elements in the consolidated financial statements
            if pattern_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                  or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                  or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
                found_match = True
                # this takes care of having two entries for marketable securities, accounts receivables as in Goldman Sachs
                # so if the entry is already in the master dict, then we add to it (as in we've found before same entry, so we add to it)
                # TODO: this should be from consolidated data
                if normalized_category in master_dict.keys():
                    master_dict[normalized_category] += int(scraped_value) if scraped_value != '—' else 0
                else:
                    master_dict[normalized_category] = int(scraped_value) if scraped_value != '—' else 0

                if 'Allowances for Doubtful Accounts' in normalized_category:
                    master_dict[normalized_category] = pattern_match.groups()[-1]

                # if 'Cash Flow Statement' in normalized_category: # TODO beware _ and : normalize!
                #     master_dict[normalized_category+'_'+pattern_match.string.split(':')[-1]] = scraped_value

    if not found_match and (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                            or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                            or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
        print('No match for ' + scraped_name)

for scraped_name, scraped_value in flatten(all_in_one_dict_gilead).items():
    for normalized_category, pattern in flatten(fin_reg.financial_entries_regex_dict).items():
        if isinstance(pattern, Pattern):
            if re.search(pattern, scraped_name) and not (re.search(fin_reg.balance_sheet_regex, scraped_name, re.IGNORECASE)
                                  or re.search(fin_reg.income_statement_regex, scraped_name, re.IGNORECASE)
                                  or re.search(fin_reg.cash_flow_statement_regex, scraped_name, re.IGNORECASE)):
                           # TODO: this should be from consolidated data
                if normalized_category not in master_dict.keys():
                    master_dict[normalized_category] = int(scraped_value) if scraped_value != '—' else 0



pprint(master_dict)

balance_sheet = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Balance Sheet', i)}
income_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Income Statement', i)}
cash_flow_statement = {i: master_dict[i] for i in master_dict.keys() if re.search(r'Cash Flow Statement', i)}
# pprint(balance_sheet)