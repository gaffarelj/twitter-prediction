from project import tw_elements as TE
import unittest
import pytest


class test_actions(unittest.TestCase):
	def test_add_list_to_empty(self):
		ac = TE.actions("testU")
		new_ac = [1, 2]
		ac.add_actions(new_ac)
		self.assertEqual(len(ac), 2)

	def test_add_list_to_full(self):
		ac = TE.actions("testU", tweets=[0, 1])
		new_ac = [3, 4]
		ac.add_actions(new_ac)
		self.assertEqual(len(ac), 4)

	def test_add_actions_to_full(self):
		ac = TE.actions("testU", tweets=[0, 1])
		new_ac = TE.actions("testU", tweets=[2, 3])
		ac.add_actions(new_ac)
		self.assertEqual(len(ac), 4)

	def test_remove_actions_from_empty(self):
		ac = TE.actions("testU", tweets=[])
		ac.remove_action(0)
		self.assertEqual(ac.tweets, [])

	def test_remove_actions_from_full(self):
		ac = TE.actions("testU", tweets=[0, 1, 5])
		ac.remove_action(0)
		self.assertEqual(ac.tweets, [1, 5])

	def test_remove_no_existing_actions_from_full(self):
		ac = TE.actions("testU", tweets=[0, 1, 5])
		ac.remove_action(2)
		self.assertEqual(ac.tweets, [0, 1, 5])

	def test_index(self):
		ac = TE.actions("testU", tweets=[0, 1, 5])
		ac.remove_action(2)
		self.assertEqual(ac[2], 5)