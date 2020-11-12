from project import twitter_api as TAPI
import unittest
import pytest
import datetime


class test_date_from_string(unittest.TestCase):
	def test_1(self):
		d = datetime.datetime(2020, 1, 7, 16, 15, 10, tzinfo=datetime.timezone.utc)
		d_f = TAPI.extract_twitter_time("Tue Jan 07 16:15:10 +0000 2020")
		self.assertEqual(d_f, d)

	def test_2(self):
		d_f = TAPI.extract_twitter_time("Bla bla bla")
		self.assertEqual(d_f, None)

	def test_3(self):
		d = datetime.datetime(1020, 1, 1, 16, 15, 10, tzinfo=datetime.timezone.utc)
		d_f = TAPI.extract_twitter_time("Wed Jan 01 16:15:10 +0000 1020")
		self.assertEqual(d_f, d)