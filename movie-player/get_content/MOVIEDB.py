
from typing import List, Dict, Tuple, Optional
import urllib3 
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup as bs



class GetData :

	def __init__(self, search : str, movie=True):
		self.search = search
		self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"

		self.BASE_URL = "https://www.themoviedb.org/search/movie"
	def check_valid_page(self, soup : bs) -> bool:
		match_list : List[str] = []
		for match in soup.find_all('p') :
			match_list.append(match.string)
		return not "There are no TV shows that matched your query." in match_list or not "There are no movies that matched your query." in match_list

	def make_req(self, page=1) -> bs:
		http = urllib3.PoolManager()
		headers = {'user-agent' : self.USER_AGENT}
		url = urljoin(self.BASE_URL, "?query={}&page={}".format(quote(self.search, safe=''), page))
		req = http.request("GET", url, headers=headers)
		assert (req.status == 200)
		soup = bs(req.data, 'html.parser')
		if self.check_valid_page(soup) :
			return soup
		raise InvalidPage("Please choose a valid page number .") 

	def get_info_content(self, page : int = 1)  :
			result  : Dict[Tuple[str, str, str]] = {}
			soup = self.make_req(page)
			film_detail = soup.find_all('div', {'class' : 'wrapper'})

			for num, detail in enumerate(film_detail, start=1) :
				if 'movie' in detail.find('a').get('href').split('/'):
					result[num] = (
					detail.find_all('h2')[0].string, # title
					detail.find('a').get('href').split('/')[2] , # id
					detail.find_all('span', {'class' : 'release_date'})[0].string if detail.find_all('span', {'class' : 'release_date'}) else "unknown" # release date
					)
			return result

class InvalidPage(Exception):
	pass
