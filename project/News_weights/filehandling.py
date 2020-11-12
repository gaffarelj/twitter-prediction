"""
All the functions that handle file reading and writing.
"""

import csv
import os
import queue
import typing as tp
from .NewsSite import NewsSite


def read_internet_tv_csv(mainpy=True) -> dict:
    """
    Reads News_weights/data/Internet_TV_per_country.csv into a usable dictionary
    @param mainpy: boolean to indicate if this file is run from main.py
    @return: dictionary containing internet and tv usage in each country
    """
    # Get the path
    if not mainpy:
        path = 'News_weights/data/Internet_TV_per_country.csv'
    else:
        path = 'project/News_weights/data/Internet_TV_per_country.csv'

    # Read the file
    with open(path) as f:
        data = list(csv.DictReader(f))

    # Extract all the data into a readable dictionary
    result = {}
    for line in data:
        if line['Name']:
            result[line['Name'].replace('~', ',')] = {
                'Internet': int(line['Users']),
                'TV': int(line['TV']),
                'pop': int(line['Population'])
            }

        if line['TV Name']:
            result[line['TV Name'].replace('~', ',')] = {
                'Internet': int(line['Users']),
                'TV': int(line['TV']),
                'pop': int(line['Population'])
            }

    return result


def write_to_csv(readers_dict: dict, mainpy=True) -> None:
    """
    Writes the readers_dict to a csv file
    @param readers_dict: dictionary with total readers of newspapers per country
    @param mainpy: boolean to indicate if this file is run from main.py
    """
    # Get the path
    if not mainpy:
        path = 'News_weights/data/readers_dict.csv'
    else:
        path = 'project/News_weights/data/readers_dict.csv'

    # Open the csv and write the readers_dict to it
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'country,number\n')
        [f.write(f'{country.replace(",","~")},{number}\n') for country, number in readers_dict.items()]


def read_from_csv(mainpy=True) -> dict:
    """
    Reads the readers_dict.csv file into readers_dict
    @param mainpy: boolean to indicate if this file is run from main.py
    @return: dictionary with total readers of newspapers per country
    """
    # Get the path
    if not mainpy:
        path = 'News_weights/data/readers_dict.csv'
    else:
        path = 'project/News_weights/data/readers_dict.csv'

    # Open the csv and read into the readers_dict
    with open(path, encoding='utf-8') as f:
        readers_dict = {}
        data = csv.DictReader(f)
        for line in data:
            readers_dict[line['country']] = int(line['number'])

    return readers_dict


def write_to_json(q_newssites: queue.Queue, num: int, mainpy=True) -> queue.Queue:
    """
    Function to write a queue with NewsSite objects to a json file
    @param q_newssites: a queue with NewsSite objects
    @param mainpy: boolean to indicate if this file is run from main.py
    @param num: the number put behind the file name
    """
    newssites = []                              # Initiate an empty list
    q_copy = queue.Queue()                      # Initiate a replacement queue
    while not q_newssites.empty():              # Iterate through the queue
        newssite, *a = q_newssites.get()            # Unpack each item
        q_copy.put((newssite,))                     # Put the newssite back
        newssites.append(newssite)                  # Also add it to the list
    NewsSite.write_json(newssites, json_idx=num, main=mainpy)    # Write the list to a json

    return q_copy                               # Return the replacement


def read_from_json(num: int, mainpy=True) -> queue.Queue:
    """
    Reads a json containing a queue of NewsSite objects
    @param num: the number put behind the file name
    @param mainpy: boolean to indicate if this file is run from main.py
    @return: a queue of NewsSite objects
    """
    q_newssites = queue.Queue()                     # Initiate queue
    newssites = NewsSite.get_json(json_idx=num, main=mainpy)     # Read the info from the json
    [q_newssites.put((newssite,)) for newssite in newssites]    # Put that all into the queue

    return q_newssites                              # Return the queue


def write_results(q_newssites: queue.Queue, mainpy=True) -> None:
    """
    Write the final results queue to the csv file
    @param q_newssites: a queue of NewsSite objects
    @param mainpy: boolean to indicate if this file is run from main.py
    """
    # Get the path
    if not mainpy:
        path = 'News_weights/data/News_reach2.csv'
    else:
        path = 'project/News_weights/data/News_reach2.csv'

    # Create the csv file
    with open(path, 'w', encoding='utf-8') as f:
        f.write('ggl_name,bng_name,reach\n')
        # Add all the newspapers to the csv
        while not q_newssites.empty():
            (newssite,) = q_newssites.get()
            if (newssite.check_flag('ggl_name') and not newssite.ggl_name == ''
                    and newssite.check_flag('bng_name') and not newssite.bng_name == ''):
                f.write(
                    f'{newssite.ggl_name.replace(",", "~")},{newssite.bng_name.replace(",", "~")},{newssite.readers}\n')

            elif newssite.check_flag('ggl_name') and not newssite.ggl_name == '':
                f.write(f'{newssite.ggl_name.replace(",", "~")},#,{newssite.readers}\n')

            elif newssite.check_flag('bng_name') and not newssite.bng_name == '':
                f.write(
                    f'#,{newssite.bng_name.replace(",", "~")},{newssite.readers}\n')


def read_from_file(mainpy: bool) -> tp.Tuple[dict, dict]:
    """
    Reads the data file containing news outlet reach data
    @param mainpy: boolean to indicate if this file is run from main.py
    @return: Integers denoting reach in Dictionary with keys: {News site names}
    """
    # Get the path
    if not mainpy:
        path = 'News_weights/data/News_reach2.csv'
    else:
        path = 'project/News_weights/data/News_reach2.csv'

    # Get the data from the file
    with open(path, encoding='utf-8') as f:
        data = list(csv.DictReader(f))

    # Create the output dictionary
    ggl_dict = {}
    bng_dict = {}
    for ln in data:
        ggl_name = ln['ggl_name'].replace('~', ',')
        bng_name = ln['bng_name'].replace('~', ',')
        if ggl_name not in ggl_dict or int(ln['reach']) > ggl_dict[ggl_name]:
            ggl_dict[ggl_name] = int(ln['reach'])
        if bng_name not in bng_dict or int(ln['reach']) > bng_dict[bng_name]:
            bng_dict[bng_name] = int(ln['reach'])

    return ggl_dict, bng_dict
