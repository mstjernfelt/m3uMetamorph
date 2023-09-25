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
                self.subfolder = self._get_series_subfolder_from_tvgname(self.name)
                self.filename = self._get_series_filename_from_tvgname(self.name) + ".strm"

            match = re.search(r'VOD:|\[VOD\]|(VOD)', extinf)
            if match:
                self.type = TypeEnum.Movie

                self.title = self._get_movie_title_from_tvgname(self.name)
                self.subfolder = self._get_movie_filename_from_tvgname(self.name)                
                self.filename = self._get_movie_filename_from_tvgname(self.name) + ".strm"

            if not self.type:
                self.type = TypeEnum.Other
                self.title = self._get_series_title_from_tvgname(self.name)
                self.include = False

    def _regex_search(self, pattern, value):
        match = re.search(pattern, value)
        if match:
            return(match.group(1))

    def _get_movie_title_from_tvgname(self, tvgname):
        pattern = r"\s*\[[^\]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    def _get_movie_filename_from_tvgname(self, tvgname):
        pattern = r"\[(?!\d{4}\])[^]]*\]"
        match = re.sub(pattern, "", tvgname)

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match)

        return(match)

    def _get_series_title_from_tvgname(self, tvgname):
        pattern = r'^(.*?) S\d+'
        match = re.search(pattern, tvgname)

        if match:
            title = match[1]
        else:
            return('')
        
        return(title)

    def _get_series_subfolder_from_tvgname(self, tvgname):
        pattern = r'^(.*?)\bS\d{1,2}'
        match = re.match(pattern, tvgname)

        if match:
            subfolder = match[0]
        else:
            return('')

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match[0])

        return(subfolder)

    def _get_series_filename_from_tvgname(self, tvgname):
        pattern = r'^.*S\d{2}\s+(.*)$'
        match = re.search(pattern, tvgname)

        if match:
            filename = match[1]
        else:
            return('')

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match[0])

        return(filename)

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
    _m3u_entries_other = [ExtM3U_Entry]
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
    m3u_entries_other: List[ExtM3U_Entry] = []
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
                self.m3u_entries_other.append(m3u_entry)
            else:
                self.m3u_entries.append(m3u_entry)

            dialog.update(percent=progress, message=m3u_entry.title)

        dialog.close

    def dumpjson(self, m3u_entries, file_name):
        m3u_dict = []

        for m3u_entry in m3u_entries:
            m3u_dict.append(m3u_entry.dictionary)

        with open(file_name, 'w') as json_file:
            json.dump(m3u_dict, json_file, indent=4)

    def generate_extm3u_other_file(self):
        try:
            filename = Utils.get_tv_output_path()
            LogManagement.info(f'Writing tv m3u: {filename}')

            if os.path.exists(filename):
                os.remove(filename)

            with open(filename, 'w', encoding='utf-8') as f:
                for m3u_entry in self.m3u_entries_other:
                    if not m3u_entry.include:
                        self.num_other_skipped += 1
                        continue

                    extinf_line = f'#EXTINF:-1 tvg-id="{m3u_entry.id}" tvg-name="{m3u_entry.name}" tvg-logo="{m3u_entry.logo}" group-title="{m3u_entry.group_title}",{m3u_entry.title}\n'
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

            if m3u_entry.type == TypeEnum.Series:
                output_path = Utils.get_series_output_path()
                output_path = os.path.join(output_path, f'{m3u_entry.title}/{m3u_entry.subfolder}')
            elif m3u_entry.type == TypeEnum.Movie:
                output_path = Utils.get_movie_output_path()
                output_path = os.path.join(output_path, f'{m3u_entry.subfolder}')

            output_strm = os.path.join(output_path, m3u_entry.filename)

            if self.preview:
                continue

            if not xbmcvfs.exists(output_strm):
                if not xbmcvfs.exists(output_path):
                    xbmcvfs.mkdir(output_path)

                try:
                    with open(output_strm, 'w', encoding='utf-8') as f:
                        f.write(m3u_entry.url)

                        if m3u_entry.type == TypeEnum.Series:
                            self.num_new_series += 1
                        elif m3u_entry.type == TypeEnum.Movie:
                            self.num_new_movies += 1

                except Exception as e:
                    LogManagement.error(e.with_traceback)
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
            LogManagement.info(f'Found {len(self.play_list_data)} entries to process.')
            
            self.play_list_data = self._get_extinf_urls(Utils.get_playlist_path())
            LogManagement.info(f'Found {len(self.play_list_data)} entries to process.')
        else:
            LogManagement.info(f'Found {len(self.play_list_data)} differences to process.')

            self.play_list_data = self._diffs(current_playlist_path=current_playlist_path, new_playlist_path=Utils.get_playlist_path())

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