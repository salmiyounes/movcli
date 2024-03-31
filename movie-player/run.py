#! /usr/bin/env python3

from typing import Tuple, Optional
import os, sys, time
from threading import Thread
from multiprocessing import Process
from pyfzf.pyfzf import FzfPrompt
from tqdm import tqdm
from colorama import Fore
from utils.extract import ExtractMovie, GetStream, RC4DecodeError, CouldntFetchKeys
from Player.play import MpvPlayer, NoSuchPlayerFound
from get_content.MOVIEDB import GetData, InvalidPage

class Main:
	def __init__(self) :
		self.__athor__ = 'salmi@younes'
	def banner(self):
		print (f'''
{Fore.YELLOW}
\t\t ███▄ ▄███▓ ▒█████   ██▒   █▓ ▄████▄   ██▓     ██▓
\t\t▓██▒▀█▀ ██▒▒██▒  ██▒▓██░   █▒▒██▀ ▀█  ▓██▒    ▓██▒
\t\t▓██    ▓██░▒██░  ██▒ ▓██  █▒░▒▓█    ▄ ▒██░    ▒██▒
\t\t▒██    ▒██ ▒██   ██░  ▒██ █░░▒▓▓▄ ▄██▒▒██░    ░██░
\t\t▒██▒   ░██▒░ ████▓▒░   ▒▀█░  ▒ ▓███▀ ░░██████▒░██░
\t\t░ ▒░   ░  ░░ ▒░▒░▒░    ░ ▐░  ░ ░▒ ▒  ░░ ▒░▓  ░░▓  
\t\t░  ░      ░  ░ ▒ ▒░    ░ ░░    ░  ▒   ░ ░ ▒  ░ ▒ ░
\t\t░      ░   ░ ░ ░ ▒       ░░  ░          ░ ░    ▒ ░
\t\t       ░       ░ ░        ░  ░ ░          ░  ░ ░  
\t\t                          ░   ░                    
\t\t                         	{Fore.WHITE}	{self.__athor__}
                         ''')
		return None

	def print_movies_list(self, page : int = 1, search = None, clear : bool = False) -> Optional[Tuple[str, str]]:
		try :
			if clear:
				os.system('clear')
			search : str = str(input(f'{Fore.RED}> Enter your query : {Fore.GREEN}')) if search is None else search
			fetch_movies = GetData(search.strip().lower(), movie=True).get_info_content(page)
			result : List[str] = []
			page_number : int =  1
			for number, (title, _id, date) in tqdm(fetch_movies.items()) :
				result.append(f'{number}- {title} {date} id : {_id}')
			time.sleep(2)
			result.extend(['next page', 'previos page', 'new search', 'quit'])
			user_prompt : str = FzfPrompt().prompt(result, '--reverse')

			if user_prompt[-1] == 'next page':
				page += 1
				self.print_movies_list(page, search, True)
			elif user_prompt[-1] == 'previos page':
				if page > 1:
					page -= 1
					return self.print_movies_list(page, search, True)
				else :
					return self.print_movies_list(page=1, search=search, clear=True)
				pass
			elif user_prompt[-1] == 'quit':
				sys.exit()
			elif user_prompt[-1] == 'new search':
				return self.print_movies_list(page=1, clear=True)
			else:
				user_prompt = user_prompt[0].split()
				return  (' '.join(user_prompt) ,user_prompt[-1])
			return None, None
		except InvalidPage as e :
			print (f'{Fore.RED}Could not find any result .', end ='\n')
			sys.exit()

	def get_stream(self, title = None, m_id  = None) -> None :
		title, m_id = self.print_movies_list() if (title is None and m_id is None) else (title, m_id)

		assert m_id is not None 

		m = ExtractMovie(m_id)
		data_id = m.get_data_id()
		sources = m.get_sources(data_id)

		encoded_url : str = m.get_encoded_stream_url(sources)
		decoded_url : str = m.decode_stream_url(encoded_url)
		make_choice : List[str] = ['Watch', 'Download']
		user_prompt : str = FzfPrompt().prompt(make_choice, '--reverse')
		if user_prompt[0] == 'Watch':
			m3u8_file = GetStream().get_m3u8_file(decoded_url)
			assert m3u8_file is not None
			list_of_choices : List[str] = ['Quit', 'New Search']
			play = Process(target=MpvPlayer().mpv_paly, args=(title, True, m3u8_file, ))
			play.start()
			thread2 = FzfPrompt().prompt(list_of_choices, '--reverse')
			if thread2[-1] == 'Quit':
				play.kill()
			elif thread2[-1] == 'New Search':
				title, m_id = self.print_movies_list(page=1, clear=True)
				self.get_stream(title=title, m_id=m_id)
				return 
			return None
		if user_prompt[0] == 'Download':
			pass
		return None 

if __name__ == '__main__':
	try :
		Main().banner()
		Main().get_stream()
	except KeyboardInterrupt as e:
		sys.exit('\n')