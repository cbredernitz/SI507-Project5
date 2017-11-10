import unittest
from SI507project5_code import *

class Test_Request(unittest.TestCase):
	def setUp(self):
		self.client_id = CLIENT_ID
		self.client_secret = CLIENT_SECRET
		self.credsfile = open('creds.json')
		self.red_uri = REDIRECT_URI
		self.cache_contents = open("cache_contents.json")

	def test_inputs(self):
		self.assertNotEqual(self.client_id, '', 'Make sure you have a client_id set in your eventbrite_data.py file')
		self.assertNotEqual(self.client_secret, '', 'Make sure to fill out you client_secret in the eventbrite_data.py file')

	def test_token_save(self):
		self.assertIn("access_token", self.credsfile.read(), 'Checking to make sure token was saved in creds.json file')

	def test_redirect_input(self):
		self.assertNotEqual(self.red_uri, '', 'Make sure to input a redirect URI')

	def test_cache_exists(self):
		self.assertTrue(self.cache_contents, 'Checking to make sure that the content is creating a cache file')

	def test_cache_into_json(self):
		base_url = 'https://www.eventbriteapi.com/v3/events/search/'
		chi_params = {"location.address": "Chicago, IL"}
		chi_ident = create_request_identifier(base_url, chi_params)
		chi_data = Make_Eventbrite_request(base_url, chi_params)
		self.assertIn(chi_ident, CACHE_DICTION, 'Making sure that the cache identifier is added to the CACHE_DICTION')

	def tearDown(self):
			self.client_id = CLIENT_ID
			self.client_secret = CLIENT_SECRET
			self.credsfile.close()
			self.red_uri = REDIRECT_URI
			self.cache_contents.close()

if __name__ == "__main__":
	unittest.main(verbosity=2)
