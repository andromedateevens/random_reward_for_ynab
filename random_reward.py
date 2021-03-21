import json
import argparse
from functions import *

#parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--profile', default='default')
parser.add_argument('--token')
parser.add_argument('--budget_name')
parser.add_argument('--category_from_name')
parser.add_argument('--category_to_name')
parser.add_argument('--amount', type=int)
parser.add_argument('--random_threshold', type=int)
args = parser.parse_args()

profile_name = args.profile

#load profile parameters
f = open('parameters.json')
profile_list = json.load(f)
profile = profile_list[profile_name]
default = profile_list['default']

#assign params; find ids if none exist

#check for token
token = select_parameter('token', args, profile, default, profile_name)[0]
if token is None:
	raise ValueError('No security token provided! Go to https://app.youneedabudget.com/settings/developer and create one, then add it to parameters.json.')
headers = {'Authorization': 'Bearer ' + token}

#find budget_id; assume name is correct if there's a conflict
budget_name, bdgt_name_source = select_parameter('budget_name', args, profile, default, profile_name)
budget_id, bdgt_id_source = select_parameter('budget_id', args, profile, default, profile_name)
if bdgt_name_source != bdgt_id_source:
	budget_id = None
budget_id = validate_budget(budget_id, headers, budget_name)

url = f'https://api.youneedabudget.com/v1/budgets/{budget_id}'

#find category_id for both categories
month = get_current_month()
cat_from_name, cat_from_name_source = select_parameter('category_from_name', args, profile, default, profile_name)
cat_from_id, cat_from_id_source = select_parameter('category_from_id', args, profile, default, profile_name)
if cat_from_name_source != cat_from_id_source:
	cat_from_id = None
cat_from_id = validate_category(url, headers, cat_from_id, month, cat_from_name, 'category_from')

cat_to_name, cat_to_name_source = select_parameter('category_to_name', args, profile, default, profile_name)
cat_to_id, cat_to_id_source = select_parameter('category_to_id', args, profile, default, profile_name)
if cat_to_name_source != cat_to_id_source:
	cat_to_id = None
cat_to_id = validate_category(url, headers, cat_to_id, month, cat_to_name, 'category_to')

#save updated budget + category ids
new_profile_list = profile_list.copy()
if bdgt_name_source != 'args':
	new_profile_list[bdgt_name_source]['budget_id'] = budget_id
if cat_from_name_source != 'args':
	new_profile_list[cat_from_name_source]['category_from_id'] = cat_from_id
if cat_to_name_source != 'args':
	new_profile_list[cat_to_name_source]['category_to_id'] = cat_to_id

f = open('parameters.json', 'w')
with f as outfile:
	json.dump(new_profile_list, outfile, indent=4)

t_hold = select_parameter('random_threshold', args, profile, default, profile_name)[0] #random threshold
money = select_parameter('amount', args, profile, default, profile_name)[0] #amount of money to transfer, in dollars

#convert params to more usable forms
money_converted = int(money * 1000)

if __name__ == '__main__':
	
	money_moved = random_reward(url, headers,cat_from_id, cat_to_id, money_converted, t_hold)
	if money_moved:
		print("Random test passed! Money transfered.")
	else:
		print("Random test failed. No money transfered.")
	