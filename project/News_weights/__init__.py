"""
Package to gather and return a readership number for a Google/Bing News outlet.

--USAGE--
 -> call():     Use this function to get a readership number of a Google/Bing News outlet.
                Param google_news_name: a string containing a name of a Google News Outlet
                Param engine:           a string indicating the search engine which the news outlet name came from
                                        ('b', 'B', 'bing') for Bing names, ('g', 'G', 'google') for Google names.
                Param mainpy:           a boolean to indicate running from main.py
                Return: - an integer containing the readership number of the outlet,
                        - None in case: the News_reach.csv file does not exist or the given name is invalid

 -> create():   Use this function to create the necessary file to be able to use call()
                Param mainpy:           a boolean to indicate running from main.py
                Param new:              a boolean to indicate starting from fresh instead of building on previous data
                Return: - None

--NOTES--
 -> The readership numbers are rough estimates based on the circulation of physical newspapers and the viewership of
    television news channels. The numbers are all pulled from Wikipedia.
 -> After using create(), make sure to add the following to your commit:
            - project/News_weights/data/NewsSiteDump1.json
            - project/News_weights/data/NewsSiteDump2.json
            - project/News_weights/data/NewsSiteDump3.json
            - project/News_weights/data/NewsSiteDump4.json
            - project/News_weights/data/NewsSiteDump5.json
"""

from . import filehandling as fh
from . import multithreading as mt
from . import namefinders as nf
from .NewsSite import NewsSite
from . import queuehandling as qh
from . import webhandling as wh
import typing as tp
import queue


def create(mainpy: bool, new: bool, queueprint=False) -> None:
    """
    Creates the data file for use by the call() function.
    @param mainpy: boolean to indicate wheter this is running from main or not
    @param new: start all the way from fresh
    @param queueprint: boolean to print the queue sizes after the process is finished
    """
    progress = mt.ProgressThread(7)
    progress.start()

    try:
        country_dict = fh.read_internet_tv_csv(mainpy=mainpy)       # Retrieve data from first csv file

        q_newssites0 = queue.Queue() if new else fh.read_from_json(5, mainpy=mainpy)
        q_newssites1 = mt.get_newspapers(q_newssites0, country_dict)

        progress.update()

        q_newssites1 = mt.get_tvchannels(q_newssites1, country_dict)
        s1 = q_newssites1.qsize()
        q_newssites1 = qh.filter_newssites(q_newssites1)
        q_newssites1 = fh.write_to_json(q_newssites1, 1, mainpy=mainpy)
        q_newssites1, q_bypass1 = qh.split_bypass(q_newssites1, 'tempreaders')
        sq1, sb1 = q_newssites1.qsize(), q_bypass1.qsize()

        progress.update()

        q_newssites2, readers_dict = mt.get_tempreaders(q_newssites1, country_dict)
        if new:
            fh.write_to_csv(readers_dict, mainpy=mainpy)
        else:
            readers_dict = fh.read_from_csv(mainpy=mainpy)
        q_newssites2 = qh.merge_bypass(q_newssites2, q_bypass1)
        s2 = q_newssites2.qsize()
        q_newssites2 = qh.filter_newssites(q_newssites2)
        q_newssites2 = fh.write_to_json(q_newssites2, 2, mainpy=mainpy)
        q_newssites2, q_bypass2 = qh.split_bypass(q_newssites2, 'readers')
        sq2, sb2 = q_newssites2.qsize(), q_bypass2.qsize()

        progress.update()

        q_newssites3 = mt.get_readers(q_newssites2, country_dict, readers_dict)
        q_newssites3 = qh.merge_bypass(q_newssites3, q_bypass2)
        s3 = q_newssites3.qsize()
        q_newssites3 = qh.filter_newssites(q_newssites3)
        q_newssites3 = fh.write_to_json(q_newssites3, 3, mainpy=mainpy)
        q_newssites3, q_bypass3 = qh.split_bypass(q_newssites3, 'ggl_name')
        sq3, sb3 = q_newssites3.qsize(), q_bypass3.qsize()

        progress.update()

        q_newssites4, q_newssites3 = nf.get_gglnames(q_newssites3)
        q_newssites4 = qh.merge_bypass(q_newssites4, q_newssites3)
        q_newssites4 = qh.merge_bypass(q_newssites4, q_bypass3)
        s4 = q_newssites4.qsize()
        q_newssites4 = qh.filter_newssites(q_newssites4)
        q_newssites4 = fh.write_to_json(q_newssites4, 4, mainpy=mainpy)
        q_newssites4, q_bypass4 = qh.split_bypass(q_newssites4, 'bng_name')
        sq4, sb4 = q_newssites4.qsize(), q_bypass4.qsize()

        progress.update()

        q_newssites5, q_newssites4 = nf.get_bngnames(q_newssites4)
        q_newssites5 = qh.merge_bypass(q_newssites5, q_newssites4)
        q_newssites5 = qh.merge_bypass(q_newssites5, q_bypass4)
        s5 = q_newssites5.qsize()
        q_newssites5 = qh.filter_newssites(q_newssites5)
        q_newssites5 = fh.write_to_json(q_newssites5, 5, mainpy=mainpy)

        progress.update()

        fh.write_results(q_newssites5, mainpy=mainpy)

        progress.stop()

    except Exception as e:
        progress.stop()
        raise e

    if queueprint:
        print(f'Queue sizes: {s1} -> q{sq1}, b{sb1}; {s2} -> q{sq2}, b{sb2}; {s3} -> '
              f'q{sq3}, b{sb3}; {s4} -> q{sq4}, b{sb4}; {s5}')


def call(news_name: str, engine: str, mainpy=True) -> tp.Optional[int]:
    """
    Gives the estimated readership number of a news outlet if that is in the data file
    @param news_name: String containing the Google/Bing name of a news outlet
    @param engine: the search engine: ('b', 'B' or 'bing' for Bing; 'g', 'G' or 'google' for Google
    @param mainpy: boolean to indicate if this file is run from main.py
    @return: Integer with the readership number, None if that does not exist
    """
    try:                                    # Try something
        data = fh.read_from_file(mainpy)           # Read the data file
        if engine in ('g', 'G', 'google'):
            result = data[0][news_name]             # Get the readership number
            del data                                # Delete the data from memory
            return result                           # Return the result
        elif engine in ('b', 'B', 'bing'):
            result = data[1][news_name]             # Get the readership number
            del data                                # Delete the data from memory
            return result                           # Return the result
        else:
            raise ValueError(
                f'Invalid engine, should be in ("b", "B", "bing") for Bing or in ("g", "G", "google") for Google')

    except FileNotFoundError:               # If there is a FileNotFoundError
        str1 = 'The data file was not created yet.'
        str2 = 'Use News_weights.create() to create the data file first.'
        str3 = 'This requires a stable internet connection and might take a while!'
        print(f'--- {str1} {str2} {str3} ---')  # Print something
        return None                             # Return None

    except KeyError:                        # If there is a KeyError
        # print(f'--- The news site you were looking for ({news_name}) has no data. ---')   # Print something
        del data                                # Delete the data from memory
        return None                             # Return None
