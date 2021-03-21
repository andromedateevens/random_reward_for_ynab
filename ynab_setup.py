import json
from functions import *

#THIS FILE IS DEPRECATED, WILL BE REMOVED

profile = 'default'

f = open('parameters.json')
params = json.load(f)[profile]

#check for token
token = params['token']
if token is None:
	raise ValueError('No security token provided! Go to https://app.youneedabudget.com/settings/developer and create one, then add it to parameters.json.')
headers = {'Authorization': 'Bearer ' + token}

#find or validate budget id
budget_name = params['budget_name']
budget_id = params['budget_id']
budget_id = validate_budget(budget_id, headers, budget_name)
url = f'https://api.youneedabudget.com/v1/budgets/{budget_id}'

#find or validate both categories
month = get_current_month()

category_from_name = params['category_from_name']
category_from_id = params['category_from_id']
category_from_id = validate_category(url, headers, category_from_id, month, category_from_name, 'category_from')

category_to_name = params['category_to_name']
category_to_id = params['category_to_id']
category_to_id = validate_category(url, headers, category_to_id, month, category_to_name, 'category_from')

#save updated parameters to file
new_params = params.copy()
new_params['budget_id'] = budget_id
new_params['category_from_id'] = category_from_id
new_params['category_to_id'] = category_to_id

f = open('parameters.json', 'w')
with f as outfile:
	json.dump(new_params, outfile, indent=4)

print("Setup complete! Run random_reward.py to begin random rewards!")
