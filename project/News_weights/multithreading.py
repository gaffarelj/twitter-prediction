"""
All the multithreading stuff for the News_weights package.
"""

from . import webhandling as wh
from .NewsSite import NewsSite
import typing as tp
import re
import threading
import queue
import time
import sys


class ProgressThread(threading.Thread):
    """
    Subclass of threading.Thread to print the progress of a program in steps
    """
    def __init__(self, total: int):
        super().__init__(name='ProgressThread')
        self.step = 1
        self.total = total
        self.work = True
        self.t0 = time.time()

    def run(self) -> None:
        """
        Override of threading.Thread.run(self) for the printing
        """
        i = 0
        print(f'Starting process')
        while self.work and threading.main_thread().is_alive():
            sys.stdout.write(f'\rWorking: step {self.step}/{self.total}        ')
            sys.stdout.write(f'\rWorking: step {self.step}/{self.total} {i*"."}')
            sys.stdout.flush()
            i %= 5
            i += 1
            time.sleep(0.5)

        if not threading.main_thread().is_alive() and self.work:
            print(f'Stopped {self} after Interupt of MainThread')

    def stop(self) -> None:
        """
        Function to stop the thread when it is not needed anymore
        """
        sys.stdout.write(f'\rDone after {round(time.time()- self.t0, 2)}s\n')
        sys.stdout.flush()
        self.work = False

    def update(self):
        """
        Update the step counter by one
        """
        self.step += 1


class QueueThread(threading.Thread):
    """
    Subclass of threading.Thread to allow for queued input and constant amount of threads
    """
    def __init__(self, input_queue: queue.Queue, result_queue: queue.Queue,
                 task: callable, args: tuple, name=None):
        """
        Initialiser for QueueThread
        @param input_queue: a queue with input values to be processed
        @param result_queue: a queue in which the results should be put()
        @param task: the task this thread has to execute
        @param args: constant set of arguments for task
        @param name: an optional name for this thread
        """
        super().__init__(name=name)

        if type(input_queue) != queue.Queue:
            raise TypeError(f'param "input_queue" should be of type {queue.Queue}')
        if type(result_queue) != queue.Queue:
            raise TypeError(f'param "result_queue" should be of type {queue.Queue}')
        if not callable(task):
            raise TypeError(f'param "task" should be a function object')
        if type(args) != tuple:
            raise TypeError(f'param "args" should be of type {tuple}')

        self.input_queue = input_queue
        self.result_queue = result_queue
        self.task = task
        self.args = args
        self.busy = None

    def run(self) -> None:
        """
        Override of threading.Thread.run(self) to allow cycling throught the queued inputs
        """
        while not self.input_queue.empty() and threading.main_thread().is_alive():     # Iterate through the input queue
            ipt = self.input_queue.get()                        # Get an input item
            self.busy = ipt                                     # Make the busy indicator that input
            try:
                opt, *xtr, iterate = self.task(*ipt, *self.args)    # Run the task and unpack the return values
                if opt is not None:                                 # In case the main output is not None
                    # If the iterate indicator is True, try to put the output through iteration
                    if iterate:
                        for tup in opt:
                            try:
                                for key, item in tup.items():
                                    self.result_queue.put((key, item))
                            except AttributeError:
                                self.result_queue.put((tup,))
                    # Otherwise put the output in the result queue as is, including the extra output
                    else:
                        if xtr:
                            self.result_queue.put((opt, tuple(xtr)))
                        else:
                            self.result_queue.put((opt,))

            # Handle exceptions
            except TypeError as e:
                print(f'\n{self.name}: While processing {ipt}, a TypeError exception was raised: {e}')
                continue

            except ConnectionRefusedError as e:
                print(f'\n{self.name}: While processing {ipt}, a ConnectionRefusedError exception was raised: {e}\n',
                      f'\n{self.name}: ABORTING FURTHER RUN')
                break

            except ConnectionError as e:
                print(f'\n{self.name}: While processing {ipt}, a ConnectionError exception was raised: {e}')
                continue

            except Exception as e:
                print(f'\n{self.name}: While processing {ipt}, an unexpected exception was raised: {e}')
                continue

        if not threading.main_thread().is_alive() and not self.input_queue.empty():
            print(f'Stopped {self} after Interupt of MainThread')

        return

    @staticmethod
    def thread_runner(input_queue: queue.Queue, task: callable, args: tuple,
                      result_queue=None, num_threads=8) -> queue.Queue:
        """
        Staticmethod for QueuedThread to manage multithreaded workflow
        @param input_queue: a queue with input values to be processed
        @param task: a function to be executed on the input values
        @param args: tuple of constants for the task
        @param result_queue: optional queue for output of task to be put into
        @param num_threads: number of threads to be used, defaults to 8
        @return: the result_queue with the processed input put() into it
        """
        # Type handling
        if type(input_queue) != queue.Queue:
            raise TypeError(f'param "input_queue" should be of type {queue.Queue}')
        if type(result_queue) != queue.Queue and result_queue is not None:
            raise TypeError(f'param "result_queue" should be of type {queue.Queue}')
        if not callable(task):
            raise TypeError(f'param "task" should be a function object')
        if type(args) != tuple:
            raise TypeError(f'param "args" should be of type {tuple}')
        if result_queue is None:
            result_queue = queue.Queue()

        if input_queue.empty():
            return result_queue

        num_threads = min(input_queue.qsize(), num_threads)

        # Creating the threads and starting them
        threads = [QueueThread(input_queue, result_queue, task, args, name=f'Thread-{i}') for i in range(num_threads)]
        [thread.start() for thread in threads]

        # Loop to keep the rest from the code from running before threads are all done
        for thread in threads:
            thread.join()
            del thread
        del input_queue

        return result_queue


def get_newspapers(q_newssites: queue.Queue, country_dict: dict) -> queue.Queue:
    """
    Gets the newspapers in the countries in country_lst from wikipedia and returns them in a queue
    @param q_newssites: a queue to put NewsSite objects in
    @param country_dict: the working country information dictionary
    @return: q_newspapers with the addition of the newspapers found here
    """
    def construct_input_queue() -> queue.Queue:
        """
        Create a queue for GetNewspaperThread to work with as a task_queue.
        @return: a queue.Queue object containing all the wikipedia links for GetNewspaperThread to work with.
        """
        result = queue.Queue()
        for country in country_dict:
            try:
                url = wh.create_wiki_link(f'List of newspapers in {country}')
                result.put((country, url))
            except ValueError:
                continue

        return result

    def task(country: str, url: str) -> tp.Tuple[tp.Optional[tp.List[NewsSite]], bool]:
        """
        The task function for the threads to work on
        @param country: a string containing a country name
        @param url: a string containing a url for the "List of newspapers in {country}" wikipedia article
        @param rel: dictionary with already existing NewsSite objects
        @return: a list with all NewsSite objects obtained from the wikipedia article
                and the iterate boolean for QueueThread.run()
        """
        page = wh.get_webpage_html_str(url)                        # Get the webpage
        find = re.findall(r'<i><a href="/wiki/[^"]*', page)     # Find wikipedia links
        if find:                                                # If something is found
            newssites = []
            for _res in find:                                       # Go through all the findings
                # Get the newspaper name and put a corresponding NewsSite instance in the result queue
                name = _res.replace('<i><a href="/wiki/', '').replace('_', ' ')
                newssite = NewsSite(name, 'pp')
                try:
                    newssite.set_wiki_url(wh.create_wiki_link(name))
                    newssite.set_country(country)
                    newssite.acquire_wiki_date()
                    newssites.append(newssite)
                except ValueError:
                    continue

            return newssites, True

        return None, False

    # Create the input queue and process it with multithreading
    input_queue = construct_input_queue()
    return QueueThread.thread_runner(input_queue, task, tuple(), result_queue=q_newssites, num_threads=24)


def get_tvchannels(q_newssites: queue.Queue, country_dict: dict) -> queue.Queue:
    """
    Get the tv channels from the wikipedia page "List of news television channels"
    @param q_newssites: a queue to put NewsSite objects in
    @param country_dict: the working country information dictionary
    @return: q_newssites with the addition of the news channels found on wikipedia
    """
    def construct_input_queue() -> queue.Queue:
        """
        Gets all news television channels that are listed on a wiki list
        @return: a queue with NewsSite objects for further processing
        """
        url = wh.create_wiki_link('List of news television channels')  # Create the url to the wiki
        page = wh.get_webpage_html_str(url)                            # Get the webpage

        findtab = re.findall(r'(<tr>(\n.*?)*</tr>)', page)          # Find table entries in the page
        result = queue.Queue()                                      # Create a Queue

        if findtab:                                                 # If something is found
            for res in findtab:                                        # Go through all the results
                findtitle = re.search(r'title="[^"]*', res[0])              # Find the wiki title
                if findtitle is not None:                                   # If something is found
                    name = findtitle.group().replace('title="', '')             # Extract the name
                    try:
                        link = wh.create_wiki_link(name)                     # Create the wikipedia link
                        if link:                                              # Put a NewsSite instance in the queue
                            newssite = NewsSite(name, 'tv')
                            newssite.set_wiki_url(link)
                            result.put((newssite,))
                    except ValueError:
                        continue                                         # Just in case there's a bad wikipedia link
        return result

    def task(newssite: NewsSite, cntry_dict: dict) -> tp.Tuple[tp.Optional[NewsSite], bool]:
        """
        The task function for the threads to work on
        @param newssite: a NewsSite object of which the country is unknown
        @param cntry_dict: the working country information dictionary
        @return: newssite, but now processed and the iterate boolean for QueueThread.run()
        """
        # Get the webpage and add to the NewsSite object
        page = wh.get_webpage_html_str(newssite.wiki_url)
        newssite.set_page(page)
        newssite.acquire_wiki_date()

        # Find the country in the wikipedia page of the NewsSite
        find = re.findall(r'(\b[Cc]ountry\b</th><td>(<.*?>)?([^<]*))', page)
        if find:
            country = find[0][-1]
            if country in cntry_dict:
                newssite.set_country(country)

        # Filter out news sites without a country
        if newssite.check_flag('country'):
            return newssite, False
        else:
            del newssite
            return None, False

    # Create the input queue and process it with multithreading
    input_queue = construct_input_queue()
    return QueueThread.thread_runner(input_queue, task, (country_dict,), result_queue=q_newssites, num_threads=48)


def get_tempreaders(q_newssites: queue.Queue, country_dict: dict) -> tp.Tuple[queue.Queue, dict]:
    """
    Finds the raw number of readers from wikipedia
    @param q_newssites: a queue with NewsSite objects to be processed
    @param country_dict: the working country information dictionary
    @return: processed version of q_newssites, dictionary with total readers of newspapers per country
    """
    def task(site: NewsSite, cntry_dict: dict) -> tp.Union[tp.Tuple[tp.Tuple[NewsSite], str, int, bool],
                                                           tp.Tuple[None, bool]]:
        """
        The task function for the threads to work on
        @param site: a NewsSite object of which the country is unknown
        @param cntry_dict: the working country information dictionary
        @return: newssite, but now processed and a tuple with info for readers_dict
                    and the iterate boolean for QueueThread.run()
        """
        # HELPER FUNCTIONS
        def finder_newspaper() -> int:
            """
            Find the raw wikipedia number for newspaper type NewsSite objects
            @return: an int with the raw wikipedia number
            """
            if site.page is not None:
                page = site.page    # If the NewsSite already has a webpage, use that
            elif site.wiki_url is None:
                page = ''           # If the NewsSite has now wiki_url, make the page an empty string
            else:
                # Get the wikipedia page and put that in the newssite for future reference
                try:
                    page = wh.get_webpage_html_str(site.wiki_url)
                    site.set_page(page)
                except ConnectionRefusedError as e:
                    print(f'\n{e}')
                    return 0
                except ConnectionError:
                    return 0

            # Use first regex to find a circulation table entry and extract it for return
            find = re.findall(
                r'\b[cC]irculation\b.*?\n?[^0-9]*[0-9,.]+[,.][0-9]{3}',
                page)

            if find:
                res = re.search(r'[0-9,.]+[,.][0-9]{3}', find[0]).group()
                if res:
                    return int(res.replace('.', '').replace(',', ''))

            # If that failed, use second regex to find text reference to circulation numbers and return
            find = re.findall(
                r'[0-9,.]+[,.][0-9]{3} \b[cC]opies\b',
                page)

            if find:
                res = re.search(r'[0-9,.]+[,.][0-9]{3}', find[-1]).group()
                if res:
                    return int(res.replace('.', '').replace(',', ''))

            # If that failed, use third regex to find text reference to circulation numbers and return
            find = re.findall(r'\b[cC]irculation\b .{0,4} [0-9,.]+[,.][0-9]{3}', page)
            if find:
                res = re.search(r'[0-9,.]+[,.][0-9]{3}', find[-1]).group()
                if res:
                    return int(res.replace('.', '').replace(',', ''))

            return int(0.005 * cntry_dict[site.country]['pop'])  # Assume value if all else fails

        def finder_tvchannel() -> int:
            """
            Find the raw wikipedia number for tv channel type NewsSite objects
            @return: an int with the raw wikipedia number
            """
            if site.page is not None:
                page = site.page    # If the NewsSite already has a webpage, use that
            elif site.wiki_url is None:
                page = ''           # If the NewsSite has now wiki_url, make the page an empty string
            else:
                page = wh.get_webpage_html_str(site.wiki_url)  # Get the wikipedia page

            # Use first regex to find a audience share table entry and extract it for return
            find = re.findall(
                r'(\b[Aa]udience [Ss]hare\b</th><td>([0-9,.]+[,.][0-9]{3}|[0-9]{1,2}.[0-9]*%|[0-9.]+ \bmillion\b|'
                r'[0-9]+))',
                page)

            if find:
                for res in find:
                    if 'audience share' in res[0].lower():
                        if '%' in res[1]:
                            return int(float(res[1].replace('%', '')) * cntry_dict[site.country]['TV'])
                        elif 'million' in res[1]:
                            return int(float(res[1].replace(' million', '')) * 10 ** 6)
                        else:
                            try:
                                return int(res[1].replace(',', ''))
                            except ValueError:
                                continue
                    else:
                        continue

            # If that failed, use second regex to find text reference to viewership numbers and return
            find = re.findall(
                r'(([0-9,.]+ (\bmillion\b )?)(\b[Vv]iewers\b|\b[Hh]omes\b)|\b[Hh]ouseholds\b)',
                page)

            if find:
                for res in find[::-1]:
                    if 'million' in res[1]:
                        return int(float(res[1].replace(' million', '')) * 10 ** 6)
                    else:
                        try:
                            return int(res[1].replace(',', ''))
                        except ValueError:
                            continue

            return int(0.01 * cntry_dict[site.country]['TV'])  # Assume value if all else fails

        # MAIN TASK
        if site.tpe == 'pp':                # If the NewsSite is a newspaper
            number = finder_newspaper()         # Find the number
        elif site.tpe == 'tv':              # If the NewsSite is a TV channel
            number = finder_tvchannel()         # Find the number
        else:                               # If the NewsSite is of unknown type
            number = 0                          # Set the number to 0

        # If the number is not 0 (failure number) add this number to the NewsSite
        if number > 0:
            site.set_tempreaders(number)

        # Filter out stuff
        if site.check_flag('tempreaders'):
            return (site,), site.country, number, False
        else:
            del site
            return None, False

    result_queue = QueueThread.thread_runner(q_newssites, task, (country_dict,), num_threads=96)    # Run the task

    q_newssites_new = queue.Queue()     # Initiate a queue for return
    readers_dict = {}                   # Initiate a dictionary to store total readership per country

    while not result_queue.empty():     # Run through the initial result queue
        item = result_queue.get()           # Get an item
        newssite, (country, num) = item     # Unpack the item
        q_newssites_new.put(newssite)       # Put the NewsSite into the final result queue

        # Count the total readership in each country
        if country not in readers_dict:
            readers_dict[country] = 0
        readers_dict[country] += num

    return q_newssites_new, readers_dict


def get_readers(q_newssites: queue.Queue, country_dict: dict, readers_dict: dict) -> queue.Queue:
    """
    Converts the raw wikipedia number into usable numbers
    @param q_newssites: a queue with NewsSite objects to be processed
    @param country_dict: the working country information dictionary
    @param readers_dict: dictionary with total readers of newspapers per country
    @return: processed version of q_newssites
    """
    def task(newssite: NewsSite, cntry_dict: dict, rdrs_dict: dict) -> tp.Tuple[tp.Optional[NewsSite], bool]:
        """
        The task function for the threads to work on
        @param newssite: a NewsSite object of which the country is unknown
        @param cntry_dict: the working country information dictionary
        @param rdrs_dict: dictionary with total readers of newspapers per country
        @return: newssite, but now processed and the iterate boolean for QueueThread.run()
        """
        country = newssite.country      # Get the country of the newssite
        if newssite.tpe == 'pp':        # Calculate final number for newspaper
            readers = int(
                cntry_dict[country]['Internet'] * newssite.tempreaders / rdrs_dict[country])

        elif newssite.tpe == 'tv':      # Calculate final number for tv channel
            readers = int(
                cntry_dict[country]['Internet'] * newssite.tempreaders / cntry_dict[country]['TV'])
        else:
            readers = None
        newssite.set_readers(readers)   # Set the number in the NewsSite object

        # Filter
        if newssite.check_flag('readers'):
            return newssite, False
        else:
            del newssite
            return None, False

    return QueueThread.thread_runner(q_newssites, task, (country_dict, readers_dict), num_threads=128)
