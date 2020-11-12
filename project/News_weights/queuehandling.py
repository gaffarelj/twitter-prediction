"""
All functions that do filtering and bypass handling of queues
"""

import queue
import typing as tp


def filter_newssites(q_newssites: queue.Queue, get_relevant=False) -> tp.Union[queue.Queue,
                                                                               tp.Tuple[queue.Queue, dict]]:
    """
    Filter out NewsSite object from q_newssites that are duplicates
    @param q_newssites: a queue of NewsSite objects
    @param get_relevant: option to just return the relevant dictionary
    @return: the filtered queue
    """
    relevant = dict()
    while not q_newssites.empty():
        (newssite,) = q_newssites.get()
        if newssite.name not in relevant:
            relevant[newssite.name] = newssite
        else:
            other = relevant[newssite.name]
            if newssite >= other:
                relevant[newssite.name] = newssite

    q_newssites_new = queue.Queue()
    for name, newssite in relevant.items():
        q_newssites_new.put((newssite,))

    return q_newssites_new if not get_relevant else (q_newssites_new, relevant)


def split_bypass(q_newssites: queue.Queue, flag: str) -> tp.Tuple[queue.Queue, queue.Queue]:
    """
    Splits NewsSite objects that don't need further processing for the given flag
    @param q_newssites: a queue of NewsSite objects
    @param flag: one of the NewsSite flags
    @return: (a queue of NewsSite objects with the flag as False,
              a queue of NewsSite objects with the flag as True)
    """
    q_bypass = queue.Queue()
    q_newssites_new = queue.Queue()
    while not q_newssites.empty():
        (newssite,) = q_newssites.get()
        if newssite.check_flag(flag):
            q_bypass.put((newssite,))
        else:
            q_newssites_new.put((newssite,))

    return q_newssites_new, q_bypass


def merge_bypass(q_newssites: queue.Queue, q_bypass: queue.Queue) -> queue.Queue:
    """
    Merges a newssites queue with a bypass queue
    @param q_newssites: a queue of NewsSite objects that was processed
    @param q_bypass: a queue of NewsSite objects that was bypassed
    """
    q_newssites_new = queue.Queue()
    while not q_bypass.empty():
        q_newssites_new.put(q_bypass.get())
    while not q_newssites.empty():
        q_newssites_new.put(q_newssites.get())

    del q_newssites
    del q_bypass

    return q_newssites_new
