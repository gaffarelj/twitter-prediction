"""
The NewsSite class for usage in the News_weights package
"""

from . import webhandling as wh
import datetime as dt
import typing as tp
import re
import json
import os


class NewsSite:
    """
    Class to save news sites and their properties
    """
    def gen_flags(self) -> None:
        """
        Generates the flags dictionary of this NewsSite
        """
        self.flags = {
            'country': self.country is not None,
            'tempreaders': self.tempreaders is not None,
            'readers': self.readers is not None,
            'ggl_name': self.ggl_name is not None,
            'bng_name': self.bng_name is not None
        }

    def __init__(self, name: str, tpe: str):
        if type(name) != str:
            raise TypeError(f'param "name" should be of type {str}')
        if type(tpe) != str:
            raise TypeError(f'param "tpe" should be of type {str}')
        elif tpe not in ('pp', 'tv'):
            raise ValueError(f'param "tpe" should have value in: {("pp", "tv")}')

        self.name: str = name  # Name of the outlet on wikipedia
        self.tpe: str = tpe  # Is it found as a newspaper of TV channel
        self.wiki_url = None  # The url to the wikipedia page
        self.country = None  # The country of origin
        self.readers = None  # The readership number
        self.ggl_name = None  # The Google News name
        self.page = None  # Option to put wikipedia webpage in here
        self.tempreaders = None  # Place to store intermediate readership numbers
        self.wiki_date = None
        self.bng_name = None
        self.flags = None
        self.gen_flags()

    def __repr__(self):
        return (f'<NewsSite Object>: <name: {self.name},\t'
                f'country: {self.country}, tpe: {self.tpe},\t'
                f'tempreaders: {self.tempreaders},\t'
                f'readers: {self.readers},\t'
                f'ggl_name: {self.ggl_name}>')

    def __str__(self):
        return f'{self.name}: {self.readers} readers'

    def __dict__(self):
        return {
            'name': self.name, 'tpe': self.tpe,
            'wiki_url': self.wiki_url, 'country': self.country,
            'readers': self.readers, 'ggl_name': self.ggl_name,
            'page': self.page, 'tempreaders': self.tempreaders,
            'wiki_date': self.wiki_date, 'bng_name': self.bng_name
        }

    def __eq__(self, other):
        if isinstance(other, NewsSite):
            return self.__dict__() == other.__dict__()
        else:
            raise TypeError(f'Cannot compare {type(self)} with {type(other)}')

    def __comp_helper(self, other):
        """
        Helper function for __lt__, __le__, __gt__, __ge__ operator overloads
            to count flagged variables
        @param other: same as in the operator overloads
        @return: 2 ints containing the amount of True flags in both self and other
        """
        self.gen_flags(), other.gen_flags()
        self_count = len([flag for key, flag in self.flags.items() if flag])
        other_count = len([flag for key, flag in other.flags.items() if flag])

        return self_count > other_count

    def __comp_wiki_date(self, other) -> tp.Optional[int]:
        """
        Helper function for __lt__, __le__, __gt__, __ge__ operator overloads
            to compare the wikipedia page dates
        @param other: another NewsSite object
        @return: an int containing the difference between the 2 dates in days
        """
        if other.wiki_date is None:
            other.acquire_wiki_date()
        if self.wiki_date is None:
            self.acquire_wiki_date()

        return (dt.datetime.strptime(self.wiki_date, '%d %B %Y') >
                dt.datetime.strptime(other.wiki_date, '%d %B %Y'))

    def __comp_readers(self, other):
        """
        Helper function for __lt__, __le__, __gt__, __ge__ operator overloads
            to compare the readers variables
        @param other:
        @return:
        """
        if self.check_flag('readers') and other.check_flag('readers'):
            return self.readers > other.readers
        elif self.check_flag('readers'):
            return True
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, NewsSite):
            return not(other.__comp_helper(self) or other.__comp_wiki_date(self) or other.__comp_readers(self))
        else:
            raise TypeError(f'Cannot compare {type(self)} with {type(other)}')

    def __gt__(self, other):
        if isinstance(other, NewsSite):
            return self.__comp_helper(other) or self.__comp_wiki_date(other) or self.__comp_readers(other)
        else:
            raise TypeError(f'Cannot compare {type(self)} with {type(other)}')

    def __le__(self, other):
        if isinstance(other, NewsSite):
            return other < self or other == self
        else:
            raise TypeError(f'Cannot compare {type(self)} with {type(other)}')

    def __ge__(self, other):
        if isinstance(other, NewsSite):
            return self > other or self == other
        else:
            raise TypeError(f'Cannot compare {type(self)} with {type(other)}')

    def set_wiki_url(self, wiki_url: tp.Optional[str]) -> None:
        """
        Set the wikipedia url if not done in __init__
        @param wiki_url: string containing a wikipedia url
        """
        if type(wiki_url) == str or wiki_url is None:
            self.wiki_url = wiki_url
        else:
            raise TypeError(f'param "wiki_url" should be of type {str}')

    def set_country(self, country: tp.Optional[str]) -> None:
        """
        Set the country of origin if not done in __init__
        @param country: string containing the name of the country
        """
        if type(country) == str or country is None:
            self.country = country
            self.gen_flags()
        else:
            raise TypeError(f'param "country" should be of type {str}')

    def set_readers(self, readers: tp.Optional[int]) -> None:
        """
        Set the amount of readers of this news outlet
        @param readers: int containing the readership number
        """
        if type(readers) == int or readers is None:
            self.readers = readers
            self.gen_flags()
        else:
            raise TypeError(f'param "readers" should be of type {int}')

    def set_ggl_name(self, ggl_name: tp.Optional[str]) -> None:
        """
        Set the Google News name of this news outlet
        @param ggl_name: string containing the Google News name
        """
        if type(ggl_name) == str or ggl_name is None:
            self.ggl_name = ggl_name
            self.gen_flags()
        else:
            raise TypeError(f'param "ggl_name" should be of type {str}')

    def set_bng_name(self, bng_name: tp.Optional[str]) -> None:
        """
        Set the Bing News name of this news outlet
        @param bng_name: string containing the Google News name
        """
        if type(bng_name) == str or bng_name is None:
            self.bng_name = bng_name
            self.gen_flags()
        else:
            raise TypeError(f'param "bng_name" should be of type {str}')

    def set_page(self, page: tp.Optional[str]) -> None:
        """
        Add a webpage to the NewsSite for further use
        @param page: string containing the webpage
        """
        if type(page) == str or page is None:
            self.page = page
            self.gen_flags()
        else:
            raise TypeError(f'param "page" should be of type {str}')

    def set_tempreaders(self, tempreaders: tp.Optional[int]) -> None:
        """
        Set a temporary readership number
        @param tempreaders: an int containing a temporary readership number
        """
        if type(tempreaders) == int or tempreaders is None:
            self.tempreaders = tempreaders
            self.gen_flags()
        else:
            raise TypeError(f'param "tempreaders" should be of type {str}')

    def acquire_wiki_date(self) -> None:
        """
        Get the date of the last wikipedia edit of the page
        """

        def find_wiki_date(page: str) -> str:
            """
            Find the date in a wikipedia page
            @param page: a string containing a wikipedia page
            @return: a string readable by datetime
            """
            find = re.findall(r'(\bThis page was last edited on \b(([0-9]{1,2}) [a-zA-Z]+ [0-9]+))', page)
            if find:
                for res in find[::-1]:
                    if len(res[2]) == 1:
                        date = '0' + res[1]
                    else:
                        date = res[1]
                    dt.datetime.strptime(date, '%d %B %Y')

                    return date

            return dt.datetime.now().strftime('%d %B %Y')

        if self.page is not None:
            try:
                self.wiki_date = find_wiki_date(self.page)
            except Exception as e:
                self.wiki_date = dt.datetime.now().strftime('%d %B %Y')
                print(f'An unexpected exception was raised: {e}, set the date to {self.wiki_date}')

        elif self.wiki_url is not None:
            try:
                self.page = wh.get_webpage_html_str(self.wiki_url)
                self.wiki_date = find_wiki_date(self.page)
            except Exception as e:
                self.wiki_date = dt.datetime.now().strftime('%d %B %Y')
                print(f'An unexpected exception was raised: {e}, set the date to {self.wiki_date}')

        else:
            self.wiki_date = dt.datetime.now().strftime('%d %B %Y')

        self.gen_flags()

    def remove_page(self):
        """
        Remove the webpage for faster writing to json
        """
        self.page = None
        self.gen_flags()

    def check_flag(self, flag: str) -> bool:
        """
        Check the flag for a class variable
        @param flag: name of the flag (equal to the variable name without the 'self.'
        @return: a boolean indicating the flag of a class variable
        """
        if type(flag) == str:
            try:
                self.gen_flags()
                return self.flags[flag]
            except KeyError:
                raise ValueError(f'param "flag" should have one of the following values:',
                                 f'{[flag for flag in self.flags]}')
        else:
            raise TypeError(f'param "flag" should be of type {str}')

    def gen_json_str(self) -> str:
        """
        Generates the json string to be written to the json file of this NewsSite
        @return: a string containing the json dump of this NewsSites
        """
        self.remove_page()
        return json.dumps(self.__dict__(), ensure_ascii=False, indent=4, sort_keys=True, default=str)

    @staticmethod
    def get_self(json_dict: dict):
        """
        Create a NewSite from a json dumps dictionary
        @param json_dict: a json.loads dictionary
        @return: a NewsSite object containing the info from the json dumps
        """
        newssite = NewsSite(json_dict['name'], json_dict['tpe'])
        newssite.set_wiki_url(json_dict['wiki_url'])
        newssite.set_country(json_dict['country'])
        newssite.set_readers(json_dict['readers'])
        newssite.set_ggl_name(json_dict['ggl_name'])
        newssite.set_page(json_dict['page'])
        newssite.set_tempreaders(json_dict['tempreaders'])
        newssite.set_bng_name(json_dict['bng_name'])

        return newssite

    @staticmethod
    def write_json(newssites: list, json_idx=0, main=True) -> None:
        """
        Write a series of NewsSites to a json file
        @param newssites: a list of NewsSites objects to be written to a json file
        @param json_idx: index number for the json file
        @param main: boolean to indicate wheter this is running from main or not
        """
        # Type handling
        if type(newssites) != list:
            raise TypeError(f'param "newssites" should be of type {list}')
        elif any(not isinstance(newssite, NewsSite) for newssite in newssites):
            raise TypeError(f'items in "newssites" should be of type {NewsSite}')
        if type(json_idx) != int:
            raise TypeError(f'param "json_idx" shoud be of type {int}')

        # Create the file string
        file = '[\n'
        for newssite in newssites:
            json_str = newssite.gen_json_str()
            file += json_str
            file += ',\n'

        if not bool(len(newssites)):
            file += ']'
        else:
            file = f'{file[:-2]}]'

        # Get the json file path
        if not main:
            path = f'News_weights/data/NewsSiteDump{json_idx}.json'
        else:
            path = f'project/News_weights/data/NewsSiteDump{json_idx}.json'

        # Write the file string to the json file
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(file)

    @staticmethod
    def get_json(newssites=None, json_idx=0, main=True) -> list:
        """
        Opens a json file into a series of Newssites
        @param newssites: an already existing list of newssites, if wished for
        @param json_idx: the index number of the json file to be opened
        @param main: boolean to indicate wheter this is running from main or not
        @return: a list of NewsSite objects
        """
        # Type handling and initialising
        if newssites is None:
            newssites = list()
        elif type(newssites) != list:
            raise TypeError(f'param "newssites" should be of type {list}')
        elif any(not isinstance(newssite, NewsSite) for newssite in newssites):
            raise TypeError(f'items in "newssites" should be of type {NewsSite}')
        if type(json_idx) != int:
            raise TypeError(f'param "json_idx" shoud be of type {int}')

        # Get the path for the json
        if not main and not (os.path.isdir('C:/Users/Guille') or os.path.isdir('C:/Users/gaffa')):
            path = f'News_weights/data/NewsSiteDump{json_idx}.json'
        else:
            path = f'project/News_weights/data/NewsSiteDump{json_idx}.json'

        # Open the file and load with json
        with open(path, encoding='utf-8') as f:
            file = json.load(f)

        # Add all the NewsSites to the final list
        for data in file:
            newssites.append(NewsSite.get_self(data))

        return newssites
