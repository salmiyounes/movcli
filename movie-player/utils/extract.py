####################################################################################
# Description: This code is adapted from the 'vidsrc-to-resolver' by Ciarands      #
#                                                                                  #
#                 original source : https://github.com/Ciarands/vidsrc-to-resolver #
#                                                                                  #
#                                                                                  #
####################################################################################

from typing import List, Dict, Union, Optional, Tuple
import urllib3
from colorama import Fore
import sys
import re
import requests
from urllib.parse import urljoin, unquote
import json
import base64
from bs4 import BeautifulSoup as bs

class ExtractMovie:
    def __init__(self, _id: str):
        self.BASE_API   = "https://vidsrc.to/embed/movie/{}".format(_id)
        self.SOURCE_URL = "https://vidsrc.to/ajax/embed/episode/"
        self.STRAE_URL = "https://vidsrc.to/ajax/embed/source/"
        self.DEFAULT_KEY = "WXrUARXb1aDLaZjI"
        self.http = urllib3.PoolManager() 
        
    def get_data_id(self) -> str:
        try :
            req = self.http.request("GET", self.BASE_API)
            assert req.status == 200
            #  print (req.data)
            soup = bs(req.data, 'html.parser')
            data_id = soup.find('a', {'data-id' : True}).get('data-id')
            if not data_id:
                return None

            return data_id
        except AssertionError as e:
            print (f'{Fore.RED}The page requested is not available .')
            sys.exit()

    def get_sources(self, data_id : str) -> Dict:
        url : str = urljoin(self.SOURCE_URL, '{}/sources'.format(data_id))
        data = self.http.request("GET", url)
        assert data.status == 200
        data = json.loads(data.data).get('result')
        result : Dict[str, str] = {source['title'] : source['id'] for source in data}
        return result

    def get_encoded_stream_url(self, source : Dict) -> str:
        if 'Vidplay' in source.keys():
            url = urljoin(self.STRAE_URL, source['Vidplay'])
        elif 'Filemoon' in source.keys() :
            url = urljoin(self.STRAE_URL, source['Filemoon'])
        assert url is not None
        req = self.http.request("GET", url)
        assert req.status == 200
        data = json.loads(req.data).get('result').get('url')
        return data

    def decode_stream_url(self, url : str) -> str:
        encoded = Utilities.decode_base64_url_safe(url)
        decoded = Utilities.decode_data(self.DEFAULT_KEY, encoded)
        decoded_text = decoded.decode('utf-8')

        return unquote(decoded_text)


class GetStream(ExtractMovie) :
    def __init__(self) :
        super().__init__(self)
        self.PROVIDER_URL = 'https://vidplay.online'

    def get_futoken(self, key : str , url : str) -> str :
        req = requests.get(urljoin(self.PROVIDER_URL, '/futoken'), {"Referer": url})
        fu_key = re.search(r"var\s+k\s*=\s*'([^']+)'", req.text).group(1)
        return f"{fu_key},{','.join([str(ord(fu_key[i % len(fu_key)]) + ord(key[i])) for i in range(len(key))])}"

    def get_m3u8_file(self, url : str) -> Optional[Tuple[List, List]]:
        url_data = url.split('?')
        v_id : str = url_data[0].split('/e/')[-1]
        key = Utilities.encode_id(v_id)
        futoken = self.get_futoken(key, url)
        req = self.http.request('GET', urljoin(self.PROVIDER_URL, f'/mediainfo/{futoken}?{url_data[1]}&autostart=true'), headers={'Referer' : url})

        assert req.status == 200 
        sources = json.loads(req.data).get('result').get('sources')
        m3u8_file = [value.get('file') for value in sources]
        return m3u8_file[0], url

class Download(ExtractMovie):

    def __init__(self):
        super().__init__(self)
        import m3u8 
        import tqdm

    def download(self, url : str, title : str) -> None:
        pass

class Utilities:
    KEY_URL : str = "https://github.com/Ciarands/vidsrc-keys/blob/main/keys.json"
    def check_os() -> str:
        import sys
        return sys.platform
    def encode_id(v_id: str) -> str:
        req = requests.get(Utilities.KEY_URL)
        text = req.text

        if req.status_code != 200:
            raise CouldntFetchKeys("Failed to fetch decryption keys!")
        matches = re.search(r"\"rawLines\":\s*\[\"(.+)\"\]", text)
        if not matches:
            raise CouldntFetchKeys("Failed to extract rawLines from keys page!")

        key1, key2 = json.loads(matches.group(1).replace("\\", ""))
        decoded_id = Utilities.decode_data(key1, v_id)
        encoded_result = Utilities.decode_data(key2, decoded_id)
        
        encoded_base64 = base64.b64encode(encoded_result)
        decoded_result = encoded_base64.decode("utf-8")

        return decoded_result.replace("/", "_")

    def decode_data(key: str, data: Union[bytearray, str]) -> bytearray:
        key_bytes = bytes(key, 'utf-8')
        s = bytearray(range(256))
        j = 0

        for i in range(256):
            j = (j + s[i] + key_bytes[i % len(key_bytes)]) & 0xff
            s[i], s[j] = s[j], s[i]

        decoded = bytearray(len(data))
        i = 0
        k = 0

        for index in range(len(data)):
            i = (i + 1) & 0xff
            k = (k + s[i]) & 0xff
            s[i], s[k] = s[k], s[i]
            t = (s[i] + s[k]) & 0xff

            if isinstance(data[index], str):
                decoded[index] = ord(data[index]) ^ s[t]
            elif isinstance(data[index], int):
                decoded[index] = data[index] ^ s[t]
            else:
                raise RC4DecodeError("Unsupported data type in the input")

        return decoded

    def decode_base64_url_safe(s: str) -> bytearray:
        standardized_input = s.replace('_', '/').replace('-', '+')
        binary_data = base64.b64decode(standardized_input)
        return bytearray(binary_data)

# Errors
class RC4DecodeError(Exception):
    pass

class CouldntFetchKeys(Exception):
    pass

