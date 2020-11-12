"""
The functions that handle finding Google and Bing names
"""

import queue
import typing as tp

from project import News_api as Na


def get_gglnames(q_newssites: queue.Queue) -> tp.Tuple[queue.Queue, queue.Queue]:
    """
    Finds the Google name of all the NewsSite objects in the queue
    @param q_newssites: a queue with NewsSite objects to be processed
    @return: processed version of q_newssites
    """
    q_newssites_new = queue.Queue()                                     # Initiate the result queue
    while not q_newssites.empty():                                      # Iterate through the queue
        (newssite,) = q_newssites.get()                                     # Get NewsSite from queue
        name = newssite.name                                                # Get the name
        ggl_url = Na.News_Search_URL_Builder(name, 'g', 40, eng=False)  # Create the google url
        try:
            ggl_res = Na.News_Search(ggl_url, tme=False)                    # Do the google search
            if ggl_res:                                                         # If this yields results
                count = {}                                                          # Initiate a counter dictionary
                for res in ggl_res:                                                 # Iterate through the results
                    count[res[1]] = 1 if res[1] not in count else count[res[1]] + 1     # Do the counting

                names = []                                                          # Initiate a names list
                shares = []                                                         # Initiate a shares list
                for name, num in count.items():                                     # Iterate through the count dict
                    names.append(name)                                                # Add each name to the names list
                    shares.append(num / sum(count.values()))                          # Calculate the share of that name

                for i, share in enumerate(shares):                                  # Iterate through the shares
                    if share == max(shares) > 0.4:                                  # Return the name with highest share
                        newssite.set_ggl_name(names[i])                             # _that is above share threshold

        # Do some Exception handling
        except ConnectionRefusedError as e:
            print(f'\nEncountered a ConnectionRefusedError in the Google search: {e},',
                  f'after {q_newssites_new.qsize()} searches.')
            q_newssites.put((newssite,))
            return q_newssites_new, q_newssites

        except Exception as e:
            print(f'\nEncountered an unexpected error in the Google search: {e}')

        # Filter
        if newssite.check_flag('ggl_name'):
            q_newssites_new.put((newssite,))
        else:
            newssite.set_ggl_name('')
            q_newssites_new.put((newssite,))

    return q_newssites_new, queue.Queue()


def get_bngnames(q_newssites: queue.Queue) -> tp.Tuple[queue.Queue, queue.Queue]:
    """
    Finds the Bing name of all the NewsSite objects in the queue
    @param q_newssites: a queue with NewsSite objects to be processed
    @return: processed version of q_newssites
    """
    q_newssites_new = queue.Queue()                                     # Initiate the result queue
    while not q_newssites.empty():                                      # Iterate through the queue
        (newssite,) = q_newssites.get()                                     # Get NewsSite from queue
        name = newssite.name                                                # Get the name
        bng_url = Na.News_Search_URL_Builder(name, 'b', 40, eng=False)  # Create the google url
        try:
            bng_res = Na.News_Search(bng_url, tme=False)                    # Do the google search
            if bng_res:                                                         # If this yields results
                count = {}                                                          # Initiate a counter dictionary
                for res in bng_res:                                                 # Iterate through the results
                    count[res[1]] = 1 if res[1] not in count else count[res[1]] + 1     # Do the counting

                names = []                                                          # Initiate a names list
                shares = []                                                         # Initiate a shares list
                for name, num in count.items():                                     # Iterate through the count dict
                    names.append(name)                                                # Add each name to the names list
                    shares.append(num / sum(count.values()))                          # Calculate the share of that name

                for i, share in enumerate(shares):                                  # Iterate through the shares
                    if share == max(shares) > 0.4:                                  # Return the name with highest share
                        newssite.set_bng_name(names[i])                             # _that is above share threshold

        # Do some Exception handling
        except ConnectionRefusedError as e:
            print(f'\nEncountered a ConnectionRefusedError in the Bing search: {e},',
                  f'after {q_newssites_new.qsize()} searches.')
            q_newssites.put((newssite,))
            return q_newssites_new, q_newssites

        except Exception as e:
            print(f'\nEncountered an unexpected error in the Bing search: {e}')

        # Filter
        if newssite.check_flag('bng_name'):
            q_newssites_new.put((newssite,))
        else:
            newssite.set_bng_name('')
            q_newssites_new.put((newssite,))

    return q_newssites_new, queue.Queue()
