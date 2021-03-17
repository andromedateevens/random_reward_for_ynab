import unittest
import functions as f

from unittest.mock import patch

class testClass:
	#used to mock request responses
	def __init__(self):
		pass

	def json(self):
		return {'test':'test'}

class errorClass:
	#used to mock request responses
	def __init__(self):
		pass

	def json(self):
		return {'error':'test'}

class test_functions(unittest.TestCase):

	def test_get_current_month(self):
		with patch('arrow.utcnow') as arrow_mock:
			arrow_mock.return_value = 'test'
			self.assertEqual(f.get_current_month(), 'test')

	def test_get_from_url(self):
		with patch('requests.get') as request_mock:
			request_mock.return_value = testClass()
			self.assertEqual(f.get_from_url('url', {'header':'header'}), {'test':'test'})
			request_mock.assert_called_with('url', headers={'header':'header'})

			request_mock.return_value = errorClass()
			with self.assertRaises(RuntimeError):
				f.get_from_url('url', {'header':'header'})

	def test_get_budgets(self):
		with patch('functions.get_from_url') as patched_fxn:
			f.get_budgets({'header':'header'})

			patched_fxn.assert_called_with('https://api.youneedabudget.com/v1/budgets/', {'header':'header'})

	def test_get_category_info(self):
		with patch('functions.get_from_url') as patched_fxn:
			f.get_category_info('url', {'header':'header'}, 'cat_id', 'month')

			patched_fxn.assert_called_with('url/months/month/categories/cat_id', {'header':'header'})

	def test_get_budget_id_from_name(self):
		with patch('functions.get_budgets') as patched_fxn:
			patched_fxn.return_value = {'data':{'budgets':[{'name':'bname', 'id':'test'}]}}
			self.assertEqual(f.get_budget_id_from_name({'header':'header'}, 'bname'), 'test')
			patched_fxn.assert_called_with({'header':'header'})

			patched_fxn.return_value = {'data':{'budgets':[{'name':'not_bname', 'id':'test'}]}}
			self.assertEqual(f.get_budget_id_from_name({'header':'header'}, 'bname'), None)

	def test_get_category_id_from_name(self):
		with patch('functions.get_from_url') as patched_fxn:
			patched_fxn.return_value = {'data':{'category_groups':[{'categories':[{'name':'cname', 'id':'test'}]}]}}
			self.assertEqual(f.get_category_id_from_name('url', {'header':'header'}, 'cname'), 'test')
			patched_fxn.assert_called_with('url/categories', {'header':'header'})

			patched_fxn.return_value = {'data':{'category_groups':[{'categories':[{'name':'not_cname', 'id':'test'}]}]}}
			self.assertEqual(f.get_category_id_from_name('url', {'header':'header'}, 'cname'), None)

	def test_update_category(self):
		with patch('requests.patch') as request_mock:
			request_mock.return_value = testClass()
			self.assertEqual(f.update_category('url', {'header':'header'}, 'cat_id', 'month', {'data':'data'}), {'test':'test'})
			request_mock.assert_called_with('url/months/month/categories/cat_id', headers={'header':'header'}, json={'data':'data'})

			request_mock.return_value = errorClass()
			with self.assertRaises(RuntimeError):
				f.update_category('url', {'header':'header'}, 'cat_id', 'month', {'data':'data'})
	
	def test_add_to_category(self):
		with patch('functions.get_current_month') as get_month, patch('functions.get_category_info') as get_cat_info, patch('functions.update_category') as update_cat:
			get_month.return_value = 'month'
			get_cat_info.return_value = {'data':{'category':{'budgeted':1}}}
			self.assertTrue(f.add_to_category('url', {'header':'header'}, 'cat_id', 1))
			get_cat_info.assert_called_with('url', {'header':'header'}, 'cat_id', 'month')
			update_cat.assert_called_with('url', {'header':'header'}, 'cat_id', 'month', {'category': {'budgeted': 2}})

	def test_random_reward(self):
		with patch('functions.add_to_category') as add_to:
			add_to.return_value = True
			self.assertFalse(f.random_reward('url', {'header':'header'}, 'cat_from', 'cat_to', 1, 0))
			add_to.assert_not_called()

			self.assertTrue(f.random_reward('url', {'header':'header'}, 'cat_from', 'cat_to', 1, 1))
			add_to.assert_any_call('url', {'header':'header'}, 'cat_from',-1)
			add_to.asser_any_call('url', {'header':'header'}, 'cat_to',1)

	def test_validate_category(self):
		with patch('functions.get_category_id_from_name') as get_cat_from_name, patch('functions.get_category_info') as get_cat_info:
			get_cat_from_name.return_value = 'test'
			self.assertEqual(f.validate_category('url', {'header':'header'}, None, 'month', 'cat_name', 'cat_type'), 'test')
			get_cat_from_name.assert_called_with('url', {'header':'header'}, 'cat_name')

			get_cat_from_name.return_value = None
			with self.assertRaises(ValueError):
				f.validate_category('url', {'header':'header'}, None, 'month', 'cat_name', 'cat_type')

			get_cat_info.return_value = {'data':{'category':{'name':'cat_name'}}}
			self.assertEqual(f.validate_category('url', {'header':'header'}, 'cat_id', 'month', 'cat_name', 'cat_type'), 'cat_id')
			get_cat_info.assert_called_with('url', {'header':'header'}, 'cat_id', 'month')

			get_cat_info.return_value = {'data':{'category':{'name':'not_cat_name'}}}
			with self.assertRaises(ValueError):
				f.validate_category('url', {'header':'header'}, 'cat_id', 'month', 'cat_name', 'cat_type')

	def test_validate_budget(self):
		with patch('functions.get_budget_id_from_name') as get_bdgt_from_name, patch('functions.get_from_url') as get_url:
			get_bdgt_from_name.return_value = 'test'
			self.assertEqual(f.validate_budget(None, {'header':'header'}, 'bdgt_name'), 'test')
			get_bdgt_from_name.assert_called_with({'header':'header'}, 'bdgt_name')

			get_bdgt_from_name.return_value = None
			with self.assertRaises(ValueError):
				f.validate_budget(None, {'header':'header'}, 'bdgt_name')

			get_url.return_value = {'data':{'budget':{'name':'bdgt_name'}}}
			self.assertEqual(f.validate_budget('bdgt_id', {'header':'header'}, 'bdgt_name'), 'bdgt_id')
			get_url.assert_called_with('https://api.youneedabudget.com/v1/budgets/bdgt_id', {'header':'header'})

			get_url.return_value = {'data':{'budget':{'name':'not_bdgt_name'}}}
			with self.assertRaises(ValueError):
				f.validate_budget('bdgt_id', {'header':'header'}, 'bdgt_name')

if __name__ == '__main__':
	unittest.main()