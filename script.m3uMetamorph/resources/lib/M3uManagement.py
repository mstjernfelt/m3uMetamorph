import re
import os
import json
import xbmcgui
import xbmcvfs
from enum import Enum
from typing import List
from resources.lib.GroupManagement import Groups
from resources.lib.FileManagement import m3uFileHandler
from resources.lib import LogManagement
from resources.lib import Utils
from resources.lib import tmdb


class TypeEnum(Enum):
    Series = 'Series'
    Movie = 'Movie'
    Other = 'Other'

class ExtM3U_Entry:
    def __init__(self, extinf=None, extinf_url=None):
        self.extinf = extinf
        self.url = extinf_url
        self.id = ""
        self.name = ""
        self.title = ""
        self.subfolder = ""
        self.filename = ""
        self.logo = ""
        self.include = ""
        self.group_title = ""
        self.type: TypeEnum = None

        self._parse_extinf(extinf)

    def __str__(self):
        return f'{{ "name": "{self.name}", "type": "{self.type.value}", "logo": "{self.logo}", "group_title": "{self.group_title}", "title": "{self.title}", "subfolder": "{self.subfolder}", "filename": "{self.filename}", "include": "{self.include}", "url": "{self.url}"}}'

    @property
    def dictionary(self):
        data = {
            "name": self.name,
            "type": self.type.value,
            "group_title": self.group_title,
            "title": self.title,
            "subfolder": self.subfolder,
            "filename": self.filename,
            "include": self.include,
            "url": self.url
        }

        return data

    def _parse_extinf(self, extinf):
         if extinf:
            self.id = self._regex_search('tvg-id="([^"]*)"', extinf)
            self.name = self._regex_search('tvg-name="([^"]*)"', extinf)
            self.logo = self._regex_search('tvg-logo="([^"]*)"', extinf)
            self.group_title = self._regex_search('group-title="([^"]*)"', extinf)
            self.type = None

            match = re.search(r'Series:|\[Series\]', extinf)
            if match:
                self.type = TypeEnum.Series
                self.title = self._get_series_title_from_tvgname(self.name)
                self.subfolder = f'{self._get_series_subfolder_from_tvgname(self.name)}'                
                self.filename = self._get_series_filename_from_tvgname(self.name) + ".strm"

            match = re.search(r'VOD:|\[VOD\]|(VOD)', extinf)
            if match:
                self.type = TypeEnum.Movie

                self.title = self._get_movie_title_from_tvgname(self.name)
                self.subfolder = f'{self._get_movie_filename_from_tvgname(self.title)}'
                self.filename = self._get_movie_filename_from_tvgname(self.name) + ".strm"

            if not self.type:
                self.type = TypeEnum.Other
                self.title = self.name
                self.include = False

    def _get_media_subfolder_from_grouptitle(self, folder_name):
        # Define the regular expression pattern to match square brackets and their contents
        #pattern = r'\[.*?\]'
        
        # Remove square brackets and their contents using re.sub
        #folder_name = re.sub(pattern, '', folder_name)

        # Define the regular expression pattern to match specific substrings
        pattern = r'VOD:|\[VOD\]|(VOD)|Series:|\[Series\]'
        
        # Remove the specified substrings using re.sub
        folder_name = re.sub(pattern, '', folder_name)

        # Replace other problematic characters with underscores
        sanitized_name = re.sub(r'[@$%&\\/:\*\?"\'<>|~`#^+=\{\}\[\];!]', '_', folder_name)
        
        # Remove leading and trailing whitespace
        sanitized_name = sanitized_name.strip()
        
        # Remove leading and trailing whitespace
        sanitized_name = sanitized_name.strip()
        sanitized_name = sanitized_name.replace(".", "")

        return sanitized_name

    def _get_movie_title_from_tvgname(self, tvgname):
        pattern = r"\s*\[[^\]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    def _get_movie_filename_from_tvgname(self, tvgname):
        pattern = r"\[(?!\d{4}\])[^]]*\]"
        match = re.sub(pattern, "", tvgname)

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match)

        # Remove leading and trailing whitespace
        match = match.strip()
        match = match.replace(".", "")

        return(match)

    def _get_series_title_from_tvgname(self, tvgname):
        pattern = r'^(.*?) S\d+'
        match = re.match(pattern, tvgname)

        if not match:
            return(tvgname)

        return(match[1])
    
    def _get_series_subfolder_from_tvgname(self, tvgname):
        # Define a regular expression pattern to capture the series subfolder
        tvgname = tvgname.replace("[4K]", "")                        
        pattern = r"(.*?)S\d{2}\s(.*?)\s-\sS\d{2}E\d{2}"
        
        # Call the extract_pattern function to process the input string
        return self._extract_pattern(tvgname, pattern)

    def _get_series_filename_from_tvgname(self, tvgname):
        # Define a regular expression pattern to capture the series filename
        tvgname = tvgname.replace("[4K]", "")
        pattern = r'S\d{2}\s+(.*)'
        
        # Call the extract_pattern function to process the input string
        return self._extract_pattern(tvgname, pattern)

    def _regex_search(self, pattern, value):
        match = re.search(pattern, value)
        if match:
            return(match.group(1))

    def _extract_pattern(self, input_string, pattern):
        try:
            # Use re.search to find the first match of the pattern in the input string
            match = re.search(pattern, input_string)

            if match:
                # Extract the captured part of the string
                matched_group = match.group(1)
                matched_group = matched_group.strip()
                matched_group = matched_group.replace(".", "")
                
                # Remove problematic characters from the matched group
                matched_group = re.sub(r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]", "", matched_group)
                matched_group = matched_group.strip()
                matched_group = matched_group.replace(".", " ")
                matched_group = matched_group.replace("  ", " ")

                return matched_group
        except Exception as e:
            # Handle any exceptions that occur during matching or extraction
            # You can print an error message or perform error-specific actions here
            print(f"Error in _extract_pattern ({input_string}): {e}")

        # If no match is found or an error occurs, return an empty string
        return ''

class M3UParser:
    def __init__(self, generate_groups=None, preview=False, cleanrun=False):
        self.preview = preview
        
        self.cleanrun = cleanrun

        m3u_file_handler = m3uFileHandler()
        m3u_file_handler.get_m3u_file(_cleanrun=self.cleanrun)

        self.play_list_data = self._open_playlist_with_progress(Utils.get_playlist_path())

        self._check_for_differences(m3u_file_handler.current_playlist_path)

        self.groups = Groups(generate_groups = generate_groups, playlist_data=self.play_list_data)

    _cleanrun = None
    _play_list_data = None
    _tv_m3u_entries = [ExtM3U_Entry]
    _m3u_entries = [ExtM3U_Entry]

    ## cleanrun
    @property
    def cleanrun(self):
        return self._cleanrun

    @cleanrun.setter
    def cleanrun(self, value: bool):
        self._cleanrun = value

    ## play_list_data
    @property
    def play_list_data(self):
        return self._play_list_data

    @play_list_data.setter
    def play_list_data(self, value):
        self._play_list_data = value

    m3u_entries: List[ExtM3U_Entry] = []
    tv_m3u_entries: List[ExtM3U_Entry] = []
    num_new_series = 0
    num_new_movies = 0
    num_errors = 0
    num_series_skipped = 0
    num_movies_skipped = 0
    num_other_skipped = 0
    num_series_exists = 0
    num_movies_exists = 0

    TVGIDCONST = 'tvg-id='

    def parse(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Parsing entries in playlist...")
        count = 0

        # Create an instance of the MovieTitleManager
        tmdb_title_manager = tmdb.Title_Manager()
        tmdb_title_manager.fetch_titles()
        LogManagement.info(f'Including {len(tmdb_title_manager.titles)} from The Movie Database fetch')

        for extinf_url, extinf_line in self.play_list_data.items():
            count += 1
            progress = count * 100 // len(self.play_list_data.items())
            dialog.update(percent=progress)

            if not self.TVGIDCONST in extinf_line:
                continue

            m3u_entry = ExtM3U_Entry(extinf=extinf_line, extinf_url=extinf_url)

            # Check if group should be included
            m3u_entry.include = self.groups.check_group_inclusion(m3u_entry.group_title)

            if m3u_entry.type == TypeEnum.Other:
                self.tv_m3u_entries.append(m3u_entry)
            else:
                # Check if a specific title is in the dictionary
                if tmdb_title_manager.check_title(m3u_entry.title):
                    m3u_entry.include = False
                
                self.m3u_entries.append(m3u_entry)

            dialog.update(percent=progress, message=m3u_entry.title)

        dialog.close

    def dumpjson(self, m3u_entries, file_name):
        m3u_dict = []

        for m3u_entry in m3u_entries:
            m3u_dict.append(m3u_entry.dictionary)

        with open(file_name, 'w') as json_file:
            json.dump(m3u_dict, json_file, indent=4)

    def generate_tv_m3u_file(self):
        try:
            filename = Utils.get_tv_m3u_path()

            LogManagement.info(f'TV m3u path: {filename}')

            if xbmcvfs.exists(filename):
                xbmcvfs.delete(filename)

            with open(filename, 'w', encoding='utf-8') as f:
                for m3u_entry in self.tv_m3u_entries:
                    if not m3u_entry.include or m3u_entry.id == "":
                        self.num_other_skipped += 1
                        continue

                    extinf_line = f'#EXTINF:-1 tvg-id="{m3u_entry.id}" tvg-name="{m3u_entry.name}" tvg-logo="{m3u_entry.logo}" group-title="{m3u_entry.group_title}",{m3u_entry.title}\n'
                    if not self.preview:
                        f.write(extinf_line)
                        f.write(m3u_entry.url + '\n')
        except Exception as e:
            # Handle any exceptions, such as file I/O errors
            print(f"Error: {str(e)}")

    def create_strm(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Creating titles to output folder...")
        count = 0

        for m3u_entry in self.m3u_entries:
            count += 1

            progress = count * 100 // len(self.play_list_data.items())
            dialog.update(percent=progress)

            if not m3u_entry.include:
                if m3u_entry.type == TypeEnum.Series:
                    self.num_series_skipped += 1
                if m3u_entry.type == TypeEnum.Movie:
                    self.num_movies_skipped += 1
                if m3u_entry.type == TypeEnum.Other:
                    self.num_other_skipped += 1

                continue
            
            if m3u_entry.type == TypeEnum.Series:
                output_path = f'{Utils.get_series_output_path()}/{m3u_entry.subfolder}'
            elif m3u_entry.type == TypeEnum.Movie:
                output_path = f'{Utils.get_movie_output_path()}/{m3u_entry.subfolder}'

            output_strm = f'{output_path}/{m3u_entry.filename}'
            
            if not xbmcvfs.exists(output_strm):
                if not self.preview:
                    if not xbmcvfs.exists(output_path):
                        xbmcvfs.mkdir(output_path)

                try:
                    if not self.preview:
                        with xbmcvfs.File(output_strm, 'w') as f:
                            LogManagement.info(f'Writing file: {output_strm}')
                            f.write(m3u_entry.url)

                    if m3u_entry.type == TypeEnum.Series:
                        self.num_new_series += 1
                    elif m3u_entry.type == TypeEnum.Movie:
                        self.num_new_movies += 1

                except Exception as e:
                    self.num_errors += 1
            else:
                if m3u_entry.type == TypeEnum.Series:
                    self.num_series_exists += 1
                elif m3u_entry.type == TypeEnum.Movie:
                    self.num_movies_exists += 1
            
            dialog.update(percent=progress, message=m3u_entry.title)

        dialog.close

    def _check_for_differences(self, current_playlist_path):
        if self.cleanrun:
            self.play_list_data = self._get_extinf_urls(Utils.get_playlist_path())

            LogManagement.info(f'Found {len(self.play_list_data)} entries to process.')
        else:
            self.play_list_data = self._diffs(current_playlist_path=current_playlist_path, new_playlist_path=Utils.get_playlist_path())
            
            LogManagement.info(f'Found {len(self.play_list_data)} differences to process.')            

    def _get_extinf_urls(self, file_name):
        if not xbmcvfs.exists(file_name):
            return {}

        extinf_url_extinf_pattern = re.compile(r'#EXTINF:-1\s+(.*?)\n(http[s]?://\S+)')

        contents = self._open_playlist_with_progress(file_name)

        matches = extinf_url_extinf_pattern.findall(contents)
        extinf_url_dict = {}
        count = 0

        for match in matches:
            extinf = match[0]
            extinf_url = match[1]
            extinf_url_dict[extinf_url] = extinf

        return(extinf_url_dict)

    def _open_playlist_with_progress(self, file_path):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create('Opening file', 'Please wait while the file is being opened...')

            contents = ''

            # Open the file and read its contents
            with xbmcvfs.File(file_path, 'r') as file:
                total_bytes = file.size()
                chunk_size = int(total_bytes / 10)  # Cast to integer
                total_read = 0

                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break

                    contents += chunk
                    total_read += len(chunk)

                    # Update progress
                    progress = int((total_read / total_bytes) * 100)
                    dialog.update(progress)

            return contents

        except UnicodeDecodeError as e:
            notif_dialog = xbmcgui.Dialog()
            notif_dialog.notification(heading='Open playlist error', message=str(e), time=3)
            LogManagement.error(f'Open playlist error, {str(e)}')
        except IOError as e:
            dialog.close()

    def _diffs(self, current_playlist_path, new_playlist_path):
        currentM3uDict = self._get_extinf_urls(current_playlist_path)
        newM3uDict = self._get_extinf_urls(new_playlist_path)

        keys1 = set(currentM3uDict.keys())
        keys2 = set(newM3uDict.keys())
        diff_keys1 = keys1 - keys2
        diff_keys2 = keys2 - keys1

        diff_items1 = {k: currentM3uDict[k] for k in diff_keys1}
        diff_items2 = {k: newM3uDict[k] for k in diff_keys2}

        result = {**diff_items1, **diff_items2}

        return(result)