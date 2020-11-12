from project import tf_text as TT
from project import tw_elements as TE
import unittest
import pytest


class test_build_dataset(unittest.TestCase):
	def test_6(self):
		*t, text_arr = TT.build_dataset("Hello World, here are 6 words")
		self.assertListEqual(list(text_arr), list(range(6)))

	def test_2(self):
		*t, text_arr = TT.build_dataset("Hello World")
		self.assertListEqual(list(text_arr), list(range(2)))

class test_get_text(unittest.TestCase):
	def test_1(self):
		tw1 = TE.tweet(0, 0, 0, 0, 0, 0, "Hello world, here is a test !", 0, 0, 0, 0)
		tw2 = TE.tweet(0, 0, 0, 0, 0, 0, "And here is a tweet, also for the test :)", 0, 0, 0, 0)
		text = TT.get_text([tw1, tw2])
		self.assertEqual(text, "Hello world, here is a test ! And here is a tweet, also for the test :) ")

class test_clean_text(unittest.TestCase):
	def test_all_but_emoji(self):
		# Could've splitted this test in multiple ones, but they were made one by one on https://regex101.com/
		text = "RT @someGuy: It's.... all a hoax !!! @AnotherGuy #NotImpeached &amp; I have proof https://this-is-some-proof"
		cleaned = TT.clean_text(text)
		self.assertEqual(cleaned, "It's all a hoax !!! and I have proof")

	def test_emoji(self):
		text = "RT @someGuy: It's.... all a hoax 💥 !!! @AnotherGuy #NotImpeached &amp; I have proof https://this-is-some-proof"
		cleaned = TT.clean_text(text)
		self.assertEqual(cleaned, "")