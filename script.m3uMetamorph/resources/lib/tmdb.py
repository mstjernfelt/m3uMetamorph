from urllib.request import Request, urlopen
from resources.lib import LogManagement
from resources.lib import Utils
import json
import xbmcgui

class Title_Manager:
    def __init__(self):
        self.titles = {}
        self.counter = 0
    
    # Fetch titles from different APIs
    base_urls = [
        "https://api.themoviedb.org/3/movie/upcoming?language=en-US&page=",
        "https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=",
        "https://api.themoviedb.org/3/movie/popular?language=en-US&page="
    ]

    headers = {
        "accept": "application/json",
        "Authorization": f'Bearer {Utils.get_setting("tmdb_api_token")}'
    }

    def fetch_titles(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Fetching The Movie Database Titles...")
        count = 0

        for base_url in self.base_urls:
            # Get the total number of pages
            req = Request(base_url + "1", headers=self.headers)
            response = urlopen(req).read().decode('utf-8')
            total_pages = json.loads(response)['total_pages']
            
            tmdb_num_pages_to_include = Utils.get_setting("tmdb_num_pages_to_include") + 1

            # Loop through the pages and add titles to the dictionary
            for page in tmdb_num_pages_to_include:  # Loop through 10 pages
                count += 1
                progress = count * 100 // tmdb_num_pages_to_include
                dialog.update(percent=progress)

                url = base_url + str(page)
                req = Request(url, headers=self.headers)
                response = urlopen(req).read().decode('utf-8')
                json_data = json.loads(response)['results']
                
                for item in json_data:
                    self.counter += 1  # Increment the counter
                    self.titles[self.counter] = item

            dialog.update(percent=progress, message=base_url)

        dialog.close                    
        
        LogManagement.info(f'Fetched {self.counter} titles from The Movie Database')                    
    
    def check_title(self, title):
        for self.counter, data in self.titles.items():
            if title.lower() in data["original_title"].lower():
                return True
        
        return False
