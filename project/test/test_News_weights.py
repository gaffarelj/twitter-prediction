"""
Test module of the News_weights package
---------------------------------------

Executes unit tests for most functions that do not require online access.

List of functions that are tested per module:
    - NewsSite.py
        > NewsSite.gen_flags(), NewsSite.check_flag(flag),
        > NewsSite.remove_page(), NewsSite.gen_json_str()
        > All set_{variable}() functions of class NewsSite
        > All operator overloading of class NewsSite

    - webhandling.py
        > create_wiki_link(art_title)
        > get_webpage_html_str(url)

    - queuehandling.py
        > filter_newssites(q_newssites)
        > split_bypass(q_newssites, flag)
        > merge_bypass(q_newssites, q_bypass_

    - multithreading.py
        > QueueThread.thread_runner(...)
"""

import unittest
from unittest.mock import patch

from project.News_weights import filehandling as fh
from project.News_weights import multithreading as mt
from project.News_weights import namefinders as nf
from project.News_weights.NewsSite import NewsSite
from project.News_weights import queuehandling as qh
from project.News_weights import webhandling as wh

import queue
import random


class TestNewsSite(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create a bunch of NewsSite objects to cover various scenarios
        """
        # Create some new NewsSites
        self.newssite_base1 = NewsSite('base1', 'pp')
        self.newssite_base2 = NewsSite('base2', 'tv')
        self.refflags_base = {
            'country': False,
            'tempreaders': False,
            'readers': False,
            'ggl_name': False,
            'bng_name': False
        }

        # Create some NewsSites with set self.country
        self.newssite_ctry1 = NewsSite('ctry1', 'pp')
        self.newssite_ctry2 = NewsSite('ctry2', 'tv')
        self.newssite_ctry1.set_country('country1')
        self.newssite_ctry2.set_country('country2')
        self.refflags_ctry = {
            'country': True,
            'tempreaders': False,
            'readers': False,
            'ggl_name': False,
            'bng_name': False
        }

        # Create some NewsSites with set self.tempreaders
        self.newssite_temp1 = NewsSite('temp1', 'pp')
        self.newssite_temp2 = NewsSite('temp2', 'tv')
        self.newssite_temp1.set_country('country1')
        self.newssite_temp2.set_country('country2')
        self.newssite_temp1.set_tempreaders(1234)
        self.newssite_temp2.set_tempreaders(1234)
        self.refflags_temp = {
            'country': True,
            'tempreaders': True,
            'readers': False,
            'ggl_name': False,
            'bng_name': False
        }

        # Create some NewsSites with set self.readers
        self.newssite_read1 = NewsSite('read1', 'pp')
        self.newssite_read2 = NewsSite('read2', 'tv')
        self.newssite_read1.set_country('country1')
        self.newssite_read2.set_country('country2')
        self.newssite_read1.set_tempreaders(1234)
        self.newssite_read2.set_tempreaders(1234)
        self.newssite_read1.set_readers(12340)
        self.newssite_read2.set_readers(12340)
        self.refflags_read = {
            'country': True,
            'tempreaders': True,
            'readers': True,
            'ggl_name': False,
            'bng_name': False
        }

        # Create some NewsSites with set self.ggl_name
        self.newssite_ggl1 = NewsSite('ggl1', 'pp')
        self.newssite_ggl2 = NewsSite('ggl2', 'tv')
        self.newssite_ggl3 = NewsSite('ggl3', 'pp')
        self.newssite_ggl4 = NewsSite('ggl4', 'tv')
        self.newssite_ggl1.set_country('country1')
        self.newssite_ggl2.set_country('country2')
        self.newssite_ggl3.set_country('country3')
        self.newssite_ggl4.set_country('country4')
        self.newssite_ggl1.set_tempreaders(1234)
        self.newssite_ggl2.set_tempreaders(1234)
        self.newssite_ggl3.set_tempreaders(1234)
        self.newssite_ggl4.set_tempreaders(1234)
        self.newssite_ggl1.set_readers(12340)
        self.newssite_ggl2.set_readers(12340)
        self.newssite_ggl3.set_readers(12340)
        self.newssite_ggl4.set_readers(12340)
        self.newssite_ggl1.set_ggl_name('ggl1')
        self.newssite_ggl2.set_ggl_name('ggl2')
        self.newssite_ggl3.set_ggl_name('')
        self.newssite_ggl4.set_ggl_name('')
        self.refflags_ggl = {
            'country': True,
            'tempreaders': True,
            'readers': True,
            'ggl_name': True,
            'bng_name': False
        }

        # Create some NewsSites with set self.bng_name
        self.newssite_bng1 = NewsSite('bng1', 'pp')
        self.newssite_bng2 = NewsSite('bng2', 'tv')
        self.newssite_bng3 = NewsSite('bng3', 'pp')
        self.newssite_bng4 = NewsSite('bng4', 'tv')
        self.newssite_bng1.set_country('country1')
        self.newssite_bng2.set_country('country2')
        self.newssite_bng3.set_country('country3')
        self.newssite_bng4.set_country('country4')
        self.newssite_bng1.set_tempreaders(1234)
        self.newssite_bng2.set_tempreaders(1234)
        self.newssite_bng3.set_tempreaders(1234)
        self.newssite_bng4.set_tempreaders(1234)
        self.newssite_bng1.set_readers(12340)
        self.newssite_bng2.set_readers(12340)
        self.newssite_bng3.set_readers(12340)
        self.newssite_bng4.set_readers(12340)
        self.newssite_bng1.set_ggl_name('ggl1')
        self.newssite_bng2.set_ggl_name('ggl2')
        self.newssite_bng3.set_ggl_name('')
        self.newssite_bng4.set_ggl_name('')
        self.newssite_bng1.set_bng_name('bng1')
        self.newssite_bng2.set_bng_name('bng2')
        self.newssite_bng3.set_bng_name('')
        self.newssite_bng4.set_bng_name('')
        self.refflags_bng = {
            'country': True,
            'tempreaders': True,
            'readers': True,
            'ggl_name': True,
            'bng_name': True
        }
        self.refjson_bng1 = '{\n    "bng_name": "bng1",\n    "country": "country1",\n    "ggl_name": "ggl1",\n    '\
                            '"name": "bng1",\n    "page": null,\n    "readers": 12340,\n    "tempreaders": 1234,\n    '\
                            '"tpe": "pp",\n    "wiki_date": null,\n    "wiki_url": null\n}'

    def tearDown(self) -> None:
        """
        Remove all the created NewsSites as cleanup
        """
        del self.newssite_base1
        del self.newssite_base2

        del self.newssite_ctry1
        del self.newssite_ctry2

        del self.newssite_temp1
        del self.newssite_temp2

        del self.newssite_read1
        del self.newssite_read2

        del self.newssite_ggl1
        del self.newssite_ggl2
        del self.newssite_ggl3
        del self.newssite_ggl4

        del self.newssite_bng1
        del self.newssite_bng2
        del self.newssite_bng3
        del self.newssite_bng4

    def test_gen_flags(self):
        self.assertEqual(self.newssite_base1.flags, self.refflags_base)
        self.assertEqual(self.newssite_base2.flags, self.refflags_base)

        self.assertEqual(self.newssite_ctry1.flags, self.refflags_ctry)
        self.assertEqual(self.newssite_ctry2.flags, self.refflags_ctry)

        self.assertEqual(self.newssite_temp1.flags, self.refflags_temp)
        self.assertEqual(self.newssite_temp2.flags, self.refflags_temp)

        self.assertEqual(self.newssite_read1.flags, self.refflags_read)
        self.assertEqual(self.newssite_read2.flags, self.refflags_read)

        self.assertEqual(self.newssite_ggl1.flags, self.refflags_ggl)
        self.assertEqual(self.newssite_ggl2.flags, self.refflags_ggl)
        self.assertEqual(self.newssite_ggl3.flags, self.refflags_ggl)
        self.assertEqual(self.newssite_ggl4.flags, self.refflags_ggl)

        self.assertEqual(self.newssite_bng1.flags, self.refflags_bng)
        self.assertEqual(self.newssite_bng2.flags, self.refflags_bng)
        self.assertEqual(self.newssite_bng3.flags, self.refflags_bng)
        self.assertEqual(self.newssite_bng4.flags, self.refflags_bng)

    def test_comp(self):
        self.assertEqual(self.newssite_base1 == self.newssite_base1, True)
        self.assertEqual(self.newssite_base1 == self.newssite_bng1, False)
        self.assertEqual(self.newssite_bng1 == self.newssite_bng1, True)
        self.assertEqual(self.newssite_bng1 == self.newssite_bng2, False)

        self.assertEqual(self.newssite_base1 > self.newssite_base2, False)
        self.assertEqual(self.newssite_base1 < self.newssite_base2, True)

        self.assertEqual(self.newssite_base1 >= self.newssite_base2, False)
        self.assertEqual(self.newssite_bng1 >= self.newssite_base1, True)

        self.assertEqual(self.newssite_base1 <= self.newssite_base2, True)
        self.assertEqual(self.newssite_bng1 <= self.newssite_base1, False)

    def test_set_wiki_url(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.set_wiki_url(1234)
            self.newssite_base1.set_wiki_url(('string',))

        self.newssite_base1.set_wiki_url('string')
        self.newssite_base2.set_wiki_url(None)
        self.assertEqual(self.newssite_base1.wiki_url, 'string')
        self.assertIsNone(self.newssite_base2.wiki_url)

    def test_set_country(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.set_country(1234)
            self.newssite_base1.set_country(('string',))

        self.newssite_base1.set_country('string')
        self.newssite_base2.set_country(None)
        self.assertEqual(self.newssite_base1.country, 'string')
        self.assertIsNone(self.newssite_base2.country)

    def test_set_readers(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.set_readers('string')
            self.newssite_base1.set_readers((1234,))

        self.newssite_base1.set_readers(1234)
        self.newssite_base2.set_readers(None)
        self.assertEqual(self.newssite_base1.readers, 1234)
        self.assertIsNone(self.newssite_base2.readers)

    def test_set_ggl_name(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.set_ggl_name(1234)
            self.newssite_base1.set_ggl_name(('string',))

        self.newssite_base1.set_ggl_name('string')
        self.newssite_base2.set_ggl_name(None)
        self.assertEqual(self.newssite_base1.ggl_name, 'string')
        self.assertIsNone(self.newssite_base2.ggl_name)

    def test_set_bng_name(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.set_bng_name(1234)
            self.newssite_base1.set_bng_name(('string',))

        self.newssite_base1.set_bng_name('string')
        self.newssite_base2.set_bng_name(None)
        self.assertEqual(self.newssite_base1.bng_name, 'string')
        self.assertIsNone(self.newssite_base2.bng_name)

    def test_set_remove_page(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.set_page(1234)
            self.newssite_base1.set_page(('string',))

        self.newssite_base1.set_page('string')
        self.newssite_base2.set_page(None)
        self.assertEqual(self.newssite_base1.page, 'string')
        self.assertIsNone(self.newssite_base2.page)

        self.newssite_base1.remove_page()
        self.newssite_base2.remove_page()
        self.assertIsNone(self.newssite_base1.page)
        self.assertIsNone(self.newssite_base2.page)

    def test_check_flag(self):
        with self.assertRaises(TypeError):
            self.newssite_base1.check_flag(1234)
            self.newssite_base1.check_flag(None)
            self.newssite_base1.check_flag(('string',))

        with self.assertRaises(ValueError):
            self.newssite_base1.check_flag('string')

        self.assertFalse(self.newssite_base1.check_flag('country'))
        self.assertFalse(self.newssite_ctry1.check_flag('tempreaders'))
        self.assertFalse(self.newssite_temp1.check_flag('readers'))
        self.assertFalse(self.newssite_read1.check_flag('ggl_name'))
        self.assertFalse(self.newssite_ggl1.check_flag('bng_name'))

        self.assertTrue(self.newssite_ggl3.check_flag('ggl_name'))
        self.assertTrue(self.newssite_bng3.check_flag('bng_name'))

        self.assertTrue(self.newssite_bng1.check_flag('country'))
        self.assertTrue(self.newssite_bng1.check_flag('tempreaders'))
        self.assertTrue(self.newssite_bng1.check_flag('readers'))
        self.assertTrue(self.newssite_bng1.check_flag('ggl_name'))
        self.assertTrue(self.newssite_bng1.check_flag('bng_name'))

    def test_gen_json_str(self):
        json_str = self.newssite_bng1.gen_json_str()
        self.assertEqual(json_str, self.refjson_bng1)


class TestWebhandling(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create some known good and known bad wikipedia links
        """
        self.wiki_good1 = 'Wat Si Khom Kham'
        self.wiki_link1 = 'https://en.wikipedia.org/wiki/Wat_Si_Khom_Kham'

        self.wiki_good2 = 'Somis, California'
        self.wiki_link2 = 'https://en.wikipedia.org/wiki/Somis,_California'

        self.wiki_good3 = 'Virpi Lummaa'
        self.wiki_link3 = 'https://en.wikipedia.org/wiki/Virpi_Lummaa'

        self.wiki_bad1 = 'sdghql'
        self.wiki_bad2 = 'Afdghjkadlgh asgdhad'

    def tearDown(self) -> None:
        """
        Remove all links and titles as cleanup
        """
        del self.wiki_good1
        del self.wiki_link1
        del self.wiki_good2
        del self.wiki_link2
        del self.wiki_good3
        del self.wiki_link3
        del self.wiki_bad1
        del self.wiki_bad2

    def test_create_wiki_link(self):
        self.assertEqual(self.wiki_link1, wh.create_wiki_link(self.wiki_good1))
        self.assertEqual(self.wiki_link2, wh.create_wiki_link(self.wiki_good2))
        self.assertEqual(self.wiki_link3, wh.create_wiki_link(self.wiki_good3))

        with self.assertRaises(ValueError):
            wh.create_wiki_link(self.wiki_bad1)
            wh.create_wiki_link(self.wiki_bad2)

        with self.assertRaises(TypeError):
            wh.create_wiki_link(1234)
            wh.create_wiki_link(('string',))

    def test_get_webpage_html_str_succes(self):
        with patch('project.News_weights.wh.rq.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = 'succes'

            self.assertEqual(wh.get_webpage_html_str(self.wiki_good1), 'succes')
            mock_get.assert_called_with(self.wiki_good1, timeout=(61, 121))

    def test_get_webpage_html_str_notfound(self):
        with patch('project.News_weights.wh.rq.get') as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.content = 'not found'

            with self.assertRaises(ConnectionError):
                wh.get_webpage_html_str(self.wiki_bad1)
                mock_get.assert_called_with(self.wiki_bad1, timeout=(61, 121))

    def test_get_webpage_html_str_toomany(self):
        with patch('project.News_weights.wh.rq.get') as mock_get:
            mock_get.return_value.status_code = 429
            mock_get.return_value.content = 'too many requests'

            with self.assertRaises(ConnectionRefusedError):
                wh.get_webpage_html_str('https://overloaded.com')
                mock_get.assert_called_with('https://overloaded.com', timeout=(61, 121))

    def test_get_webpage_html_str_TypeHandle(self):
        with patch('project.News_weights.wh.rq.get') as mock_get:
            with self.assertRaises(TypeError):
                wh.get_webpage_html_str(1234)
                wh.get_webpage_html_str((self.wiki_bad2,))


class TestQueuehandling(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create some queues with NewsSites to test with
        """
        random.seed(5264782435)
        # A queue with filled NewsSites and no doubles
        self.q_newssites1 = queue.Queue()
        for i in range(20):
            newssite = NewsSite(f'test{i}_1', 'pp')
            newssite.set_country(f'test{i}_1')
            newssite.set_tempreaders(random.randint(0, 1000000000))
            newssite.set_readers(random.randint(1,7) * newssite.tempreaders)
            newssite.set_ggl_name(f'test{i}_1')
            newssite.set_bng_name(f'test{i}_1')
            self.q_newssites1.put((newssite,))

        self.result1 = {'country': 20, 'tempreaders': 20, 'readers': 20,
                        'ggl_name': 20, 'bng_name': 20, 'total': 20, 'double': 0}

        # A queue with partially filled NewsSites and no doubles
        self.q_newssites2 = queue.Queue()
        for i in range(30):
            newssite = NewsSite(f'test{i}_2', 'pp')
            if i >= 5:
                newssite.set_country(f'test{i}_2')
            if i >= 10:
                newssite.set_tempreaders(random.randint(0, 1000000000))
            if i >= 15:
                newssite.set_readers(random.randint(1,7) * newssite.tempreaders)
            if i >= 20:
                newssite.set_ggl_name(f'test{i}_2')
            if i >= 25:
                newssite.set_bng_name(f'test{i}_2')

            self.q_newssites2.put((newssite,))

        self.result2 = {'country': 25, 'tempreaders': 20, 'readers': 15,
                        'ggl_name': 10, 'bng_name': 5, 'total': 30, 'double': 0}

        # A queue with filled NewsSites and doubles
        self.q_newssites3 = queue.Queue()
        for i in range(20):
            newssite = NewsSite(f'test{i}_3', 'pp')
            newssite.set_country(f'test{i}_3')
            newssite.set_tempreaders(random.randint(0, 1000000000))
            newssite.set_readers(random.randint(1, 7) * newssite.tempreaders)
            newssite.set_ggl_name(f'test{i}_3')
            newssite.set_bng_name(f'test{i}_3')
            self.q_newssites3.put((newssite,))

        for i in range(5):
            newssite = NewsSite(f'test{i}_3', 'pp')
            newssite.set_country(f'test{i}_3')
            newssite.set_tempreaders(random.randint(0, 1000000000))
            newssite.set_readers(random.randint(1, 7) * newssite.tempreaders)
            newssite.set_ggl_name(f'test{i}_3')
            newssite.set_bng_name(f'test{i}_3')
            self.q_newssites3.put((newssite,))

        self.result3 = {'country': 25, 'tempreaders': 25, 'readers': 25,
                        'ggl_name': 25, 'bng_name': 25, 'total': 25, 'double': 5}

        # A queue with partially filled NewsSites and doubles
        self.q_newssites4 = queue.Queue()
        for i in range(30):
            newssite = NewsSite(f'test{i}_4', 'pp')
            if i >= 5:
                newssite.set_country(f'test{i}_4')
            if i >= 10:
                newssite.set_tempreaders(random.randint(0, 1000000000))
            if i >= 15:
                newssite.set_readers(random.randint(1, 7) * newssite.tempreaders)
            if i >= 20:
                newssite.set_ggl_name(f'test{i}_4')
            if i >= 25:
                newssite.set_bng_name(f'test{i}_4')

            self.q_newssites4.put((newssite,))

        for i in range(5):
            newssite = NewsSite(f'test{i}_4', 'pp')
            newssite.set_country(f'test{i}_4')
            newssite.set_tempreaders(random.randint(0, 1000000000))
            newssite.set_readers(random.randint(1, 7) * newssite.tempreaders)
            newssite.set_ggl_name(f'test{i}_4')
            newssite.set_bng_name(f'test{i}_4')
            self.q_newssites4.put((newssite,))

        self.result4 = {'country': 30, 'tempreaders': 25, 'readers': 20,
                        'ggl_name': 15, 'bng_name': 10, 'total': 35, 'double': 5}

    @staticmethod
    def count_flag(q_newssites: queue.Queue) -> dict:
        """
        Count the amount of True flags for each flag name in a queue of NewsSites
        @param q_newssites: a queue of NewsSite objects
        @return: a dictionary with the count for each flag
        """
        count_dict = {'country': 0, 'tempreaders': 0, 'readers': 0,
                      'ggl_name': 0, 'bng_name': 0}
        while not q_newssites.empty():
            (newssite,) = q_newssites.get()

            for flag in count_dict:
                count_dict[flag] += 1 if newssite.check_flag(flag) else 0

        return count_dict

    def tearDown(self) -> None:
        """
        Remove everything created by the setUp()
        """
        del self.q_newssites1
        del self.result1

        del self.q_newssites2
        del self.result2

        del self.q_newssites3
        del self.result3

        del self.q_newssites4
        del self.result4

    def test_count_flag(self):
        count_dict1 = self.count_flag(self.q_newssites1)
        for flag in count_dict1:
            self.assertEqual(self.result1[flag], count_dict1[flag])

        count_dict2 = self.count_flag(self.q_newssites2)
        for flag in count_dict2:
            self.assertEqual(self.result2[flag], count_dict2[flag])

        count_dict3 = self.count_flag(self.q_newssites3)
        for flag in count_dict3:
            self.assertEqual(self.result3[flag], count_dict3[flag])

        count_dict4 = self.count_flag(self.q_newssites4)
        for flag in count_dict4:
            self.assertEqual(self.result4[flag], count_dict4[flag])

    def test_filter_newssites(self):
        q_newssites1_new, relevant1 = qh.filter_newssites(self.q_newssites1, get_relevant=True)
        self.assertEqual(q_newssites1_new.qsize(), self.result1['total'])
        self.assertEqual(len(relevant1), self.result1['total'])

        q_newssites3_new, relevant3 = qh.filter_newssites(self.q_newssites3, get_relevant=True)
        self.assertEqual(q_newssites3_new.qsize(), self.result3['total'] - self.result3['double'])
        self.assertEqual(len(relevant3), self.result3['total'] - self.result3['double'])

        q_newssites4_new, relevant4 = qh.filter_newssites(self.q_newssites4, get_relevant=True)
        self.assertEqual(q_newssites4_new.qsize(), self.result4['total'] - self.result4['double'])
        count_dict = self.count_flag(q_newssites4_new)
        for flag in count_dict:
            self.assertEqual(self.result4[flag], count_dict[flag])
        self.assertEqual(len(relevant4), self.result4['total'] - self.result4['double'])

    def test_split_bypass_c(self):
        q_newssites2_c, q_bypass2_c = qh.split_bypass(self.q_newssites2, 'country')
        self.assertEqual(q_newssites2_c.qsize(), self.result2['total'] - self.result2['country'])
        self.assertEqual(q_bypass2_c.qsize(), self.result2['country'])

    def test_split_bypass_t(self):
        q_newssites2_t, q_bypass_t = qh.split_bypass(self.q_newssites2, 'tempreaders')
        self.assertEqual(q_newssites2_t.qsize(), self.result2['total'] - self.result2['tempreaders'])
        self.assertEqual(q_bypass_t.qsize(), self.result2['tempreaders'])

    def test_split_bypass_r(self):
        q_newssites2_r, q_bypass2_r = qh.split_bypass(self.q_newssites2, 'readers')
        self.assertEqual(q_newssites2_r.qsize(), self.result2['total'] - self.result2['readers'])
        self.assertEqual(q_bypass2_r.qsize(), self.result2['readers'])

    def test_split_bypass_g(self):
        q_newssites2_g, q_bypass2_g = qh.split_bypass(self.q_newssites2, 'ggl_name')
        self.assertEqual(q_newssites2_g.qsize(), self.result2['total'] - self.result2['ggl_name'])
        self.assertEqual(q_bypass2_g.qsize(), self.result2['ggl_name'])

    def test_split_bypass_b(self):
        q_newssites2_b, q_bypass2_b = qh.split_bypass(self.q_newssites2, 'bng_name')
        self.assertEqual(q_newssites2_b.qsize(), self.result2['total'] - self.result2['bng_name'])
        self.assertEqual(q_bypass2_b.qsize(), self.result2['bng_name'])

    def test_merge_bypass(self):
        q_newssites12 = qh.merge_bypass(self.q_newssites1, self.q_newssites2)
        self.assertEqual(self.result1['total'] + self.result2['total'], q_newssites12.qsize())
        count_dict12 = self.count_flag(q_newssites12)
        for flag in count_dict12:
            self.assertEqual(self.result1[flag] + self.result2[flag], count_dict12[flag])

        q_newssites34 = qh.merge_bypass(self.q_newssites3, self.q_newssites4)
        self.assertEqual(self.result3['total'] + self.result4['total'], q_newssites34.qsize())
        count_dict34 = self.count_flag(q_newssites34)
        for flag in count_dict34:
            self.assertEqual(self.result3[flag] + self.result4[flag], count_dict34[flag])


class TestMultithreading(unittest.TestCase):
    def setUp(self) -> None:
        """
        Create some input and result queues to test multithreading
        """
        self.input_queue_single = queue.Queue()
        for i in range(20):
            self.input_queue_single.put((i,))

        self.input_queue_multi = queue.Queue()
        for i in range(20):
            self.input_queue_multi.put((i, f'string_{i}',))

        self.args = (5, 'string_arg')

        self.result_queue_single = queue.Queue()
        for i in range(5):
            self.result_queue_single.put((20 + i,))

        self.result_queue_multi = queue.Queue()
        for i in range(5):
            self.result_queue_multi.put((20 + i, f'string_{20 + i}',))

    @staticmethod
    def task_single_exiter(num: int, const: int, const_text: str):
        """
        A simple task to test QueueThread with single input and some optional args, outputting non-iterable stuff
        @param num: a number
        @param const: another number
        @param const_text: some string
        @return: an int, const_text, False
        """
        return num + const, const_text, False

    @staticmethod
    def task_single_initer(num: int, const: int, const_text: str):
        """
        A simple task to test QueueThread with single input and some optional args, outputting iterable stuff
        @param num: a number
        @param const: another number
        @param const_text: some string
        @return: a tuple, const_text, True
        """
        return (num + const, const), const_text, True

    @staticmethod
    def task_multi_exiter(num: int, text: str, const: int, const_text: str):
        """
        A simple task to test QueueThread with multiple inputs and some optional args, outputting non-iterable stuff
        @param num: a number
        @param text: a string
        @param const: another number
        @param const_text: some string
        @return: a string, const_text, False
        """
        return f'{text}: {num + const}', const_text, False

    @staticmethod
    def task_multi_initer(num: int, text: str, const: int, const_text: str):
        """
        A simple task to test QueueThread with multiple inputs and some optional args, outputting non-iterable stuff
        @param num: a number
        @param text: a string
        @param const: another number
        @param const_text: some string
        @return: a string, const_text, False
        """
        return (f'{text}: {num + const}', const), const_text, True

    def tearDown(self) -> None:
        """
        Remove everything created by setUp() as cleanup
        """
        del self.input_queue_single
        del self.result_queue_single
        del self.input_queue_multi
        del self.result_queue_multi
        del self.args

    def test_QueueThread_single_exiter_exresq(self):
        result = mt.QueueThread.thread_runner(self.input_queue_single, self.task_single_exiter, self.args)
        self.assertEqual(20, result.qsize())
        i = 0
        while not result.empty():
            result_item = result.get()
            ref_item = (i + self.args[0], (self.args[1],))
            self.assertEqual(ref_item, result_item)
            i += 1

    def test_QueueThread_single_exiter_inresq(self):
        result = mt.QueueThread.thread_runner(self.input_queue_single, self.task_single_exiter, self.args,
                                              result_queue=self.result_queue_single)
        self.assertEqual(25, result.qsize())
        i = 0
        while not result.empty():
            result_item = result.get()
            if i >= 5:
                ref_item = (i - 5 + self.args[0], (self.args[1],))
            else:
                ref_item = (20 + i,)

            self.assertEqual(ref_item, result_item)
            i += 1

    def test_QueueThread_single_initer_exresq(self):
        result = mt.QueueThread.thread_runner(self.input_queue_single, self.task_single_initer, self.args)
        self.assertEqual(40, result.qsize())
        i = 0
        while not result.empty():
            result_item1 = result.get()
            result_item2 = result.get()

            ref_item1 = (i + self.args[0],)
            ref_item2 = (self.args[0],)

            self.assertEqual(ref_item1, result_item1)
            self.assertEqual(ref_item2, result_item2)
            i += 1

    def test_QueueThread_multi_exiter_exresq(self):
        result = mt.QueueThread.thread_runner(self.input_queue_multi, self.task_multi_exiter, self.args)
        self.assertEqual(20, result.qsize())
        i = 0
        while not result.empty():
            result_item = result.get()
            ref_item = (f'string_{i}: {i + self.args[0]}', (self.args[1],))

            self.assertEqual(ref_item, result_item)
            i += 1

    def test_QueueThread_multi_exiter_inresq(self):
        result = mt.QueueThread.thread_runner(self.input_queue_multi, self.task_multi_exiter, self.args,
                                              result_queue=self.result_queue_multi)
        self.assertEqual(25, result.qsize())
        i = 0
        while not result.empty():
            result_item = result.get()
            if i >= 5:
                ref_item = (f'string_{i-5}: {i-5 + self.args[0]}', (self.args[1],))
            else:
                ref_item = (20 + i, f'string_{20 + i}',)

            self.assertEqual(ref_item, result_item)
            i += 1

    def test_QueueThread_multi_initer_exresq(self):
        result = mt.QueueThread.thread_runner(self.input_queue_multi, self.task_multi_initer, self.args)
        self.assertEqual(40, result.qsize())
        i = 0
        while not result.empty():
            result_item = result.get()
            ref_item = (f'string_{i}: {i + self.args[0]}',)
            self.assertEqual(ref_item, result_item)

            const_item = result.get()
            self.assertEqual((self.args[0],), const_item)
            i += 1


if __name__ == '__main__':
    unittest.main()
