from project import twitter_api_public as TAPIP
import unittest
import pytest


class test_n_from_string(unittest.TestCase):
	def test_nothing(self):
		self.assertEqual(TAPIP.n_from_string("21"), 21)
		self.assertEqual(TAPIP.n_from_string(""), 0)
		self.assertEqual(TAPIP.n_from_string("21 Hello World !"), 21)
		self.assertEqual(TAPIP.n_from_string("21 Hello World ! 37K"), 21)

	def test_K(self):
		self.assertEqual(TAPIP.n_from_string("21.4K"), 21400)
		self.assertEqual(TAPIP.n_from_string("1K"), 1000)
		self.assertEqual(TAPIP.n_from_string("21.4K Hello World !"), 21400)
		self.assertEqual(TAPIP.n_from_string("21.4K Hello World ! 37K"), 21400)

	def test_M(self):
		self.assertEqual(TAPIP.n_from_string("21.4M"), 21400000)
		self.assertEqual(TAPIP.n_from_string("1M"), 1000000)
		self.assertEqual(TAPIP.n_from_string("21.4M Hello World !"), 21400000)
		self.assertEqual(TAPIP.n_from_string("21.4M Hello World ! 37M"), 21400000)