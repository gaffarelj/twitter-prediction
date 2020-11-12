import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


'''
				*Using this module
-----------------------------------------------------------------------------------------------------------------------------------------

				1) Build the URL for the search. You can use your own or the included URL builder aka News_Search_URL_Builder()

						FUNCTION: News_Search_URL_Builder(text to search, engine to search with, news output count)
								-INPUT:
									-text to search:
									-engine to search with: For Google use either "G","g" or "google". For BING use either "b","B" or "bing" 
									-news output count: How many news articles do you want the code to search and return. Do not use very large values (over 40)
								-RETURN:
									-Search URL
								
				2) Perform a News search with the URL using function News_Search(url)
						FUNCTION: News_Search(url)
								-INPUT:
									-url:
								-RETURN:
									-Returns the news articles found in the list format:
									[[URL1, Agency1, Time1, AbsoluteTime1 Description1],[URL2, Agency2, Time2, AbsoluteTIme2, Description2],[....],...]

				3) In oder to run the search function in a separate process you can use the News_caller(url) function in main. This function should be called using:

									def News_caller(url):
										News = NAPI.News_Search(url)
										print(News)

									if __name__ == '__main__':
									    p = Process(target=News_caller, args=("search_url",))
									    p.start()
									    p.join()


							Where p is the name of the process and url is your desired url. Building the URL is quick, there is no benefit in multiprocessing that part
'''		

'''
'Known issues/ To-Do:
	-429 response exponential wait time was removed. Do we want it back?
	-Not important since we dont use the time the article was publish but bing returns the current time instead on the time the article was published.
'''

error_429_count = 0	#Starting value for too many requests (html 429) sleep-time
Test = False #Test will raise certain exeptions that are not critical. Allows the dev to notice certain issues but saves the user a few exceptions. 


#Post processing for the HTML received from a Google News search. Returns the news articles found in the list format: [[URL1, Agency1, Time1, AbsoluteTime1 Description1],[URL2, Agency2, Time2, AbsoluteTIme2, Description2],[....],...]
def Google_News_Soup_Parser(soup, tme=True):
	[x.extract() for x in soup.find_all('div', class_='YiHbdc card-section')]				#Remove sub news
	[x.extract() for x in soup.find_all('div', class_='ErI7Gd card-section')]				#Remove sub news
	main_links = soup.find_all('a', class_='l lLrAF')										#Create a list with all news links
	news_sites = soup.find_all('span', class_='xQ82C e8fRJf')								#Create a list with all news site names
	news_times = soup.find_all('span', class_='f nsa fwzPFf')								#Create a list with all news times (Format can be X minutes ago, X hours ago or DD MM. YY)
	news_descriptions = soup.find_all('div', class_='st')									#Create a list with all news descriptions (brief text extracted from the news article that shows in GN search)
	results = []
	for i in range(0,len(main_links)):
		absolute_time = datetime.now()
	#Finding the time of the publication:
		if tme:
			if news_times[i].get_text().find('hour') != -1:										#If hours is found in the time tag then we have a str of the format x hour ago. Add the hours to current time
				minutes = int(news_times[i].get_text().split(" ")[0]) * 60
				absolute_time = datetime.now() + timedelta(minutes=minutes)
			elif news_times[i].get_text().find('minute') != -1:									#If minutes is found in the time tag then we have a str of the format x minutes ago. Add the hours to current time
				minutes = int(news_times[i].get_text().split(" ")[0])
				absolute_time = datetime.now() + timedelta(minutes=minutes)
			elif news_times[i].get_text().find(',') != -1:										#Format 1 (5 nov. 2019) smallcase month + .
				absolute_time = datetime.strptime(news_times[i].get_text(), '%b %d, %Y')
			else:																				#Format 2 (5 Nov 2019) Capitaliced month and no dot
				absolute_time = datetime.strptime(news_times[i].get_text(), '%d %b %Y')

		#Append to the results list in order [Link, Site, Time, Absolute_Time, Description]
		results.append([main_links[i].get('href'), news_sites[i].get_text(), news_times[i].get_text(), absolute_time, str(news_descriptions[i].get_text()).split('\\')[0]])
	return results

#Post processing for the HTML received from a Bing News search. Returns the news articles found in the list format: [[URL1, Agency1, Time1, AbsoluteTime1 Description1],[URL2, Agency2, Time2, AbsoluteTIme2, Description2],[....],...]
def Bing_News_Soup_Parser(soup, tme=True):
	main_links_and_sites = soup.find_all('a', class_='title')			#Create a list with all news links and names
	news_times = soup.find_all('div', class_='source')					#Create a list with all news times (Format can be X minutes ago, X hours ago or DD MM. YY)
	news_descriptions = soup.find_all('div', class_='snippet')			#Create a list with all the news descriptions
	results = []
	for i in range(0,len(main_links_and_sites)):
		absolute_time = datetime.now()
		#Append to the results list in order [Link, Site, Time, Absolute_Time, Description]
		results.append([main_links_and_sites[i].get('href'), main_links_and_sites[i].get('data-author'), news_times[i], absolute_time, str(news_descriptions[i].get('title'))])
	return results

#With the URL perform a search with a custom user agent and call the right html post processing for the search (aka: Google_News_Soup_Parser or Bing_News_Soup_Parser)
def News_Search(url, tme=True):
	# Add your own browser agent, and google cookies to get the proper html response and get less 429 errors. (Too many requests)
	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4003.0 Safari/537.36 Edg/81.0.381.0'
	cookie = ""
	headers = {'user-agent': user_agent, "cookie": cookie}
	response = requests.get(url, headers=headers)	#Perform a search using a url with the modified user agent and save the html
	if response.status_code == 429: #If we get a 429 response code (Too many requests) raise an exception. The automated wait time was removed.
		raise ConnectionRefusedError(f'Request for {url} returned HTTP code 429')
	if url.find("https://www.google.com") != -1:	#If its a Google News search post process using Google_News_Soup_Parser()
		if str(response.content).find("id=\"search\"") != -1:		#Google html has a lot of crap from the headers and stuff and takes too long to parse. It can safely be splitted at id="search" so thats what we will do
			soup = BeautifulSoup(str(response.content).split("id=\"search\"")[1], "html.parser")	#Clean and save html as soup using BeautifulSoup and lxml.. As input we use a splitted version of the html response to greatly reduce the runtime for this step
		else:
			print("Error. id=search was not found")
			if Test:	#If we have test enabled stop raise an error to make sure we realice this is going on. Otherwise, if Test = False the user is executing the code and it is better to let the code parse the whole html. Slower but works
				raise NameError("News_API, id=search was not found")
			soup = BeautifulSoup(response.content, "html.parser")
		results = Google_News_Soup_Parser(soup, tme)
	elif url.find("https://www.bing.com") != -1:	#If its a Bing News search post process using Bing_News_Soup_Parser()
		soup = BeautifulSoup(response.content, "html.parser")										#Clean and save html as soup using BeautifulSoup and lxml
		results = Bing_News_Soup_Parser(soup)
	return results

#Check whether input is a tweet url. If its not build a url containing the input that will show count many results
def News_Search_URL_Builder(input, engine, count=10, eng=True):
	#If its not we build our URL from a standard google search and adding querries for searching in news, return count news, safe search active and prioritice english language
	if engine in ["G", "g", "google"]:
		Google_search_base_url = "https://www.google.com/search?q="								# Baseline google search url
		News_query = "&tbm=nws"																	# Add this query to only search news
		Num_query = "&num=" + str(count)														# Add this query to get count many results
		Safe_query = "&safe=active"																# Add this query to have google safe search active
		Language_query = "&hl=en&lr=lang_en" if eng else ''										# Add t	his query to prioritise english results
		return Google_search_base_url + '"' + str(input.replace(" ", "+")) + '"' + News_query + Num_query + Safe_query + Language_query # Adding the base, yor input with spaces replaced to + and between "" and all the queries
	elif engine in ["B", "b", "bing"]:
		Bing_search_base_url = "https://www.bing.com/news/?q="									# See https://tiny.cc/bbwahz for docs
		Num_query = "&count=" + str(count)														# count is count, same as googlr
		Safe_query = "&safeSearch=strict"														# SafeSearch for preventing no-no words on my christian minecraft server
		Language_query = "&mkt=en-US" if eng else ''											# 'mkt' means market, which is the area from which the results will be gotten
		return Bing_search_base_url + '"' + str(input.replace(" ", "+")) + '"'  + Num_query + Safe_query + Language_query # Adding the base, yor input with spaces replaced to + and between "" and all the queries