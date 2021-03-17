import json
from functions import *

f = open('parameters.json')
params = json.load(f)

token =  params['token']
budget_id = params['budget_id']
cat_from_id = params['category_from_id']
cat_to_id = params['category_to_id']
t_hold = params['random_threshold'] #random threshold
money = params['amount'] #amount of money to transfer, in dollars

#convert params to more usable forms
headers = {'Authorization': 'Bearer ' + token}
url = f'https://api.youneedabudget.com/v1/budgets/{budget_id}'
money_converted = int(money * 1000)

if __name__ == '__main__':
	
	money_moved = random_reward(url, headers,cat_from_id, cat_to_id, money_converted, t_hold)
	if money_moved:
		print("Random test passed! Money transfered.")
	else:
		print("Random test failed. No money transfered.")
	