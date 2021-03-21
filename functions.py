import random
import requests
import arrow
import json
import argparse

def get_current_month():
	"""
	Use arrow to find the current month.
	Paramters: 
		none
	Returns: time, as a string
	"""
	return arrow.utcnow().format()

def get_from_url(url, headers):
	"""
	Given a url, return the API response.
	Parameters: 
		url: string, the url
		headers: dict, the headers to send with the request to the URL
	Returns: API response, in dict form
	"""
	r = requests.get(url, headers=headers).json()
	if 'error' in r.keys():
		raise RuntimeError('API response error' + str(r))
	return r

def get_budgets(headers):
	"""
	Return API response for all budget request
	Paramters: 
		headers: dict, the headers to send with the request to the URL
	Returns: API response, in dict form
	"""
	url = 'https://api.youneedabudget.com/v1/budgets/'
	return get_from_url(url, headers)

def get_category_info(budget_url, headers, category_id, month):
	"""
	Given a category ID, return the API response corresponding to that category.
	Paramters: 
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL
		category_id: string, the category id
		month: string, the current time
	Returns: API response, in dict form
	"""
	url = budget_url + f'/months/{month}/categories/{category_id}'
	return get_from_url(url, headers)

def get_budget_id_from_name(headers, budget_name):
	"""
	Given a budget name, find the corresponding ID and return it, 
	or None if there is no such budget
	Paramters: 
		headers: dict, the headers to send with the request to the URL
		budget_name: string, the name of the budget
	Returns: budget id (string)
	"""
	budget_id = None
	budgets = get_budgets(headers)
	for budget in budgets['data']['budgets']:
		if budget['name'] == budget_name:
			budget_id = budget['id']
	return budget_id

def get_category_id_from_name(budget_url, headers, category_name):
	"""
	Given a category name, find the corresponding ID and return it, or None if there is no such budget
	Paramters: 
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL
		category_name: string, the name of the category
	Returns: category id (string)
	"""
	category_id = None
	categories = get_from_url(budget_url + '/categories', headers)
	for category_group in categories['data']['category_groups']:
		for category in category_group['categories']:
			if category['name'] == category_name:
				category_id = category['id']
	return category_id

def update_category(budget_url, headers, category_id, month, data):
	"""
	Given a category ID, update it with data. Data contains the amount budgeted
	Paramters:
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL 
		category_id: string, the category id
		month: string, the current time
		data: dict, the update for the category
	Returns: API response, in dict form
	"""
	r = requests.patch(budget_url +f'/months/{month}/categories/{category_id}', headers=headers, json=data).json()
	if 'error' in r.keys():
		raise RuntimeError('API response error' + str(r))
	return r

def add_to_category(budget_url, headers, category_id, amount):
	"""
	Given a category ID, add amount to what is already budgeted for that category
	Parameters:
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL 
		category_id: string, the category id
		amount: int, amount to add
	Returns: True (to be used by wrapper functions)
	"""

	current_month = get_current_month()

	#find amount in category
	info_response = get_category_info(budget_url, headers, category_id, current_month)
	old_budget = info_response['data']['category']['budgeted']

	#add amount to old_budget and update
	new_budget = old_budget + amount
	new_data = {'category': {'budgeted': new_budget}}
	update_response = update_category(budget_url, headers, category_id, current_month, new_data)
	return True

def random_reward(budget_url, headers, cat_from, cat_to, amount, threshold):
	"""
	Generate a random float between 0 and 1; if this number is below the threshold, 
	add amount to the category specified by category_id. Return True if money was added, 
	and False otherwise.
	Parameters: 
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL 
		cat_from: string, id of the category to take money from
		cat_to: string, id of the category to move money to
		amount: int, amount to add
		threshold: float 0 <= n <= 1
	Returns: bool, True if money added and False otherwise
	"""

	random_num = random.random()
	if random_num < threshold:
		add_to_category(budget_url, headers, cat_from, amount*-1)
		return add_to_category(budget_url, headers, cat_to, amount)
	else:
		return False

def validate_category(budget_url, headers, category_id, month, category_name, cat_type):
	"""
	Validate that category_name corresponds to category_id, or find category_id if category_id is None
	Parameters:
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL 
		category_id: string, the category id
		month: string, the current time
		category_name: string, name of the category
		cat_type: string, name of the category paramter (for use in error messages)
	Returns: Category id, as string
	"""
	if category_id is None:
		#find id
		category_id = get_category_id_from_name(budget_url, headers, category_name)
		if category_id is None:
			raise ValueError(f'{cat_type} not found! Check spelling and make sure that the budget actually exists.')
	else:
		#validate id
		category_data = get_category_info(budget_url, headers, category_id, month)
		if category_data['data']['category']['name'] != category_name:
			raise ValueError(f'{cat_type}_id does not match cateogry_from_name! Correct name or replace ID with null to get new id')

	return category_id

def validate_budget(budget_id, headers, budget_name):
	"""
	Validate that budget_name corresponds to budget_id, or find budget_id if budget_id is None
	Parameters:
		budget_url: string, the url of the budget
		headers: dict, the headers to send with the request to the URL 
		budget_name: string, name of the budget
	Returns: budget id, as string
	"""
	if budget_id is None:
		#find id
		budget_id = get_budget_id_from_name(headers, budget_name)
		if budget_id is None:
			raise ValueError('Budget not found! Check spelling and make sure that the budget actually exists.')
	else:
		#validate id
		url = f'https://api.youneedabudget.com/v1/budgets/{budget_id}'
		budget_data = get_from_url(url, headers)
		if budget_data['data']['budget']['name'] != budget_name:
			raise ValueError('budget_id does not match budget_name! Correct name or replace ID with null to get new id')

	return budget_id
	
def select_parameter(param, args, profile, default, profile_name):
	"""
	Chooses what value a parameter should have, with the priority ordering being 1) command-line argument 2) value from profile and 3) value from default.
	Parameters:
		param: string, the name of the parameter
		args: argparse Namespace, the command-line arguments
		profile: dict, the parameter values in the chosen profile
		default: dict, the paramater values in the default profile (might be same as profile)
		profile_name: str, name of the profile
	Returns: tuple, (param_value (int or string), param_source (string))
	"""
	if getattr(args, param) != None:
		param_value = getattr(args, param)
		param_source = 'args'
	elif param in profile:
		param_value = profile[param]
		param_source =  profile_name
	elif param in default:
		param_value = default[param]
		param_source = 'default'
	else:
		raise ValueError(f'No value found for {param}')
	return (param_value, param_source)