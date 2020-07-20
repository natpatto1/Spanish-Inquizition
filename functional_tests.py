from selenium import webdriver
import unittest

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_signup_and_see_data(self):
        #Go to homepage (login page)
        self.browser.get('http://localhost:8000')

        #Notices the page title includes spanish
        self.assertIn('Spanish',self.browser.title )
        #self.fail('Finish the test!')

        #She can sign up


if __name__ == '__main__':
    unittest.main(warnings='ignore')


