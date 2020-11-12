"""
Workflow functions to handle web requests for the News_weights package
"""

import requests as rq
from bs4 import BeautifulSoup as Bs


def create_wiki_link(art_title: str) -> str:
    """
    Creates a wikipedia url from a wikipedia page name
    @param art_title: wikipedia page name
    @return: wikipedia url referring to the given article
    """
    # Type handling
    if type(art_title) != str:
        raise TypeError(f'param "art_title" should be of type {str}')

    # Create the link
    wiki_link = 'https://en.wikipedia.org/wiki/' + art_title.replace(' ', '_')

    # Check if it makes sense
    page = rq.get(wiki_link, timeout=(61, 121))
    if page.status_code == 200:
        return wiki_link
    elif page.status_code == 429:
        raise ConnectionRefusedError(f'{wiki_link} could not be reached. Request returned HTTP code: 429')
    else:
        raise ValueError(f'param "art_title" does not refer to a valid wikipedia page')


def get_webpage_html_str(url: str, pretty=False) -> str:
    """
    Gets a string of the html code of the webpage from the url
    @param pretty: indicates whether to return prettified version or not
    @param url: a url of a webpage
    @return: the html code of that webpage
    """
    # Type handling
    if type(url) != str:
        raise TypeError(f'param "url" should be of type {str}')

    # Request the page, handle the HTTP codes and return the correct string form of the page
    page = rq.get(url, timeout=(61, 121))
    if page.status_code == 200:
        soup = Bs(page.content, 'html.parser')
        return str(soup) if not pretty else soup.prettify()
    elif page.status_code == 429:
        raise ConnectionRefusedError(f'{url} could not be reached. Request returned HTTP code: 429')
    else:
        raise ConnectionError(f'{url} could not be reached. Request returned HTTP code: {page.status_code}')
