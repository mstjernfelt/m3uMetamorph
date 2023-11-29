from urllib.request import Request, urlopen
import json
import xbmcgui
from resources.lib import LogManagement, Utils

class TitleManager:
    @property
    def enabled(self):
        return bool(Utils.get_setting("tmdb_enabled"))

    def __init__(self):
        self.titles = {}
        self.counter = 0
    
    tmdb_upcoming_num_pages_to_include = int(Utils.get_setting("tmdb_upcoming_num_pages_to_include"))
    tmdb_top_rated_num_pages_to_include = int(Utils.get_setting("tmdb_top_rated_num_pages_to_include"))
    tmdb_popular_num_pages_to_include = int(Utils.get_setting("tmdb_popular_num_pages_to_include"))
    tmdb_series_top_rated_num_pages_to_include = int(Utils.get_setting("tmdb_series_top_rated_num_pages_to_include"))
    tmdb_series_popular_num_pages_to_include = int(Utils.get_setting("tmdb_series_popular_num_pages_to_include"))

    if tmdb_upcoming_num_pages_to_include <= 0 or tmdb_top_rated_num_pages_to_include <= 0 or tmdb_popular_num_pages_to_include <= 0 or tmdb_series_top_rated_num_pages_to_include <= 0 or tmdb_series_popular_num_pages_to_include <= 0:
        raise ValueError("You need to specify number of pages to fetch in settings.")

    # Fetch titles from different APIs
    base_urls = [
        ("https://api.themoviedb.org/3/movie/upcoming?language=en-US&page=", "Movies: Upcoming", tmdb_upcoming_num_pages_to_include),
        ("https://api.themoviedb.org/3/movie/top_rated?language=en-US&page=", "Movies: Top Rated", tmdb_top_rated_num_pages_to_include),
        ("https://api.themoviedb.org/3/movie/popular?language=en-US&page=", "Movies: Popular", tmdb_popular_num_pages_to_include),
        ("https://api.themoviedb.org/3/tv/top_rated?language=en-US&page=", "Series: Top Rated", tmdb_series_top_rated_num_pages_to_include),
        ("https://api.themoviedb.org/3/tv/popular?language=en-US&page=", "Series: Top Rated", tmdb_series_popular_num_pages_to_include)
    ]

    headers = {
        "accept": "application/json",
        "Authorization": f'Bearer {Utils.get_setting("tmdb_api_token")}'
    }

    def fetch_titles(self):
        if not self.enabled:
            return

        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Fetching The Movie Database Titles...")

        for base_url, url_description, num_pages in self.base_urls:
            # Get the total number of pages
            req = Request(base_url + "1", headers=self.headers)
            response = urlopen(req).read().decode('utf-8')
            
            count = 0

            # Loop through the pages and add titles to the dictionary
            for page in range(1, num_pages):  # Loop through specified pages
                url = base_url + str(page)
                req = Request(url, headers=self.headers)
                response = urlopen(req).read().decode('utf-8')
                json_data = json.loads(response)['results']
                
                for item in json_data:
                    self.counter += 1  # Increment the counter
                    self.titles[self.counter] = item

                count += 1
                progress = count * 100 // (len(self.base_urls))
                dialog.update(percent=progress, message=f"Fetching {url_description} - Page {page}/{num_pages}")

        dialog.close()
        
        self.dumpjson(self.titles, "C:\BrightCom\GitHub\mstjernfelt\m3uMetamorph\local\\tmdb.json")

        LogManagement.info(f'Fetched {self.counter} titles from The Movie Database')                    
    
    def dumpjson(self, entries, file_name):
        with open(file_name, 'w') as json_file:
            json.dump(entries, json_file, indent=4)

    def check_title(self, title):
        if not self.enabled:
            return True

        for _, data in self.titles.items():
            title_fields = ["original_title", "original_name"]  # Fields to check
            
            # Check if either "original_title" or "original_name" is available
            for field in title_fields:
                if field in data and title.lower() in data[field].lower():
                    return True
        
        return False