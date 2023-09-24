import re
from resources.lib.GroupManagement import Groups
from resources.lib.FileManagement import m3uFileHandler
from resources.lib import LogManagement
from resources.lib import utils
from enum import Enum

import os
import xbmcgui
import xbmcvfs

class ExtM3UEntry:
    extinf = None
    url = None
    id = None
    name = None
    title = None
    subfolder =  None
    filename =  None
    logo =er =  None
    include = None    
    group_title = None
    type = None

    def __init__(self, extinf=None, extinf_url=None):
        self.extinf = extinf  # EXTINF extinf_line
        self.url = extinf_url

        self.parse_extinf(extinf)

    def __str__(self):
        return f'{{ "name": "{self.name}", "logo": "{self.logo}", "group_title": "{self.group_title}", "title": "{self.title}", "subfolder": "{self.subfolder}", "filename": "{self.filename}", "include": "{self.include}", "url": "{self.url}"}},'

    def parse_extinf(self, extinf):
        if extinf:
            self.id = self.regex_search('tvg-id="([^"]*)"', extinf)
            self.name = self.regex_search('tvg-name="([^"]*)"', extinf)
            self.logo = self.regex_search('tvg-logo="([^"]*)"', extinf)
            self.group_title = self.regex_search('group-title="([^"]*)"', extinf)

            self.type = None

            match = re.search(r'Series:|\[Series\]', extinf)
            if match:
                self.type = TypeEnum.Series
                
                self.title = self.get_series_title_from_tvgname(self.name)
                self.subfolder = self.get_series_subfolder_from_tvgname(self.name)
                self.filename = self.get_series_filename_from_tvgname(self.name) + ".strm"

            match = re.search(r'VOD:|\[VOD\]|(VOD)', extinf)
            if match:
                self.type = TypeEnum.Movie

                self.title = self.get_movie_title_from_tvgname(self.name)
                self.subfolder = self.get_movie_filename_from_tvgname(self.name)                
                self.filename = self.get_movie_filename_from_tvgname(self.name) + ".strm"

            if not self.type:
                self.type = TypeEnum.Other
                self.title = self.get_series_title_from_tvgname(self.name)
                self.include = False

    def regex_search(self, pattern, value):
        match = re.search(pattern, value)
        if match:
            return(match.group(1))

    # This is a movie [PRE] [2022] ->
    # This is a movie
    def get_movie_title_from_tvgname(self, tvgname):

        pattern = r"\s*\[[^\]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    # This is a movie [PRE] [2022] ->
    # This is a movie [2022]
    def get_movie_filename_from_tvgname(self, tvgname):
        pattern = r"\[(?!\d{4}\])[^]]*\]"
        match = re.sub(pattern, "", tvgname)

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match)

        return(match)

    # This is a series - S01 This is a series - S01E01
    # This is a series -
    def get_series_title_from_tvgname(self, tvgname):
        pattern = r'^(.*?) S\d+'
        match = re.search(pattern, tvgname)

        if match:
            title = match[1]
        else:
            return('')
        
        return(title)

    # This is a series - S01 This is a series - S01E01
    # This is a series - S01
    def get_series_subfolder_from_tvgname(self, tvgname):
        pattern = r'^(.*?)\bS\d{1,2}'
        match = re.match(pattern, tvgname)

        if match:
            subfolder = match[0]
        else:
            return('')

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match[0])

        return(subfolder)

    # This is a series - S01 This is a series - S01E01
    #                        This is a series - S01E01
    def get_series_filename_from_tvgname(self, tvgname):
        pattern = r'^.*S\d{2}\s+(.*)$'
        match = re.search(pattern, tvgname)

        if match:
            filename = match[1]
        else:
            return('')

        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"
        match = re.sub(pattern, "", match[0])

        return(filename)

# Define an enum class
class TypeEnum(Enum):
    Series = 'Series'
    Movie = 'Movie'
    Other = 'Other'

class m3uParser:
    m3uEntries = []
    m3uEntriesOther = []
    groups = None
    logger = None
    provider = None
    m3u_extinf_Url = None
    preview = False
    playListData = None
    cleanrun = None

    num_titles_skipped = 0
    num_new_series = 0
    num_new_movies = 0
    num_errors = 0
    num_series_skipped = 0
    num_movies_skipped = 0
    num_other_skipped = 0

    def __init__(self, _generate_groups = None, _preview=False, _cleanrun=False):

        self.preview = _preview

        self.cleanrun = _cleanrun

        m3u_file_handler = m3uFileHandler()
        m3u_file_handler.get_m3u_file(_cleanrun=self.cleanrun)

        self.playListData = self.open_file_with_progress(utils.get_playlist_path())

        self.Check_For_Differences(m3u_file_handler.current_playlist_path)

        self.groups = Groups(generate_groups = _generate_groups, playlist_data=self.playListData)
        
    def Check_For_Differences(self, _current_playlist_path):
        if self.cleanrun:
            LogManagement.info(f'Found {len(self.playListData)} entries to process.')
            
            self.playListData = self.get_extinf_urls(utils.get_playlist_path())
            LogManagement.info(f'Found {len(self.playListData)} entries to process.')
        else:
            LogManagement.info(f'Found {len(self.playListData)} differences to process.')

            self.playListData = self.diffs(current_playlist_path=_current_playlist_path, new_playlist_path=utils.get_playlist_path())

    def parse(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Parsing entries in playlist...")
        count = 0

        for extinf_url, extinf_line in self.playListData.items():
            count += 1
            progress = count * 100 // len(self.playListData.items())
            dialog.update(percent=progress)

            if not 'tvg-id=""' in extinf_line:
                continue

            m3uEntry = ExtM3UEntry(extinf=extinf_line, extinf_url=extinf_url)

            # Check if group should be included
            m3uEntry.include = self.groups.check_group_inclusion(m3uEntry.group_title)

            if m3uEntry.type == TypeEnum.Other:
                self.m3uEntriesOther.append(m3uEntry)
            else:
                self.m3uEntries.append(m3uEntry)

            dialog.update(percent=progress, message=m3uEntry.title)

        dialog.close

    def generate_extm3u_other_file(self):
        try:
            with open(utils.get_outputpath_other(), 'w', encoding='utf-8') as f:
                for entry in self.m3uEntriesOther:
                    extinf_line = f'#EXTINF:-1 tvg-id="{entry.id}" tvg-name="{entry.name}" tvg-logo="{entry.logo}" group-title="{entry.group_title}",{entry.title}\n'
                    f.write(extinf_line)
                    f.write(entry.url + '\n')
        except Exception as e:
            # Handle any exceptions, such as file I/O errors
            print(f"Error: {str(e)}")

    # Usage:
    # Replace 'm3uEntriesOther' with your list of entries and provide the desired output file path.
    # generate_extm3u_file(m3uEntriesOther, 'output.extm3u')

    def create_strm(self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Creating titles to output folder...")
        count = 0

        for m3uEntry in self.m3uEntries:
            count += 1
            progress = count * 100 // len(self.playListData.items())
            dialog.update(percent=progress)

            if not m3uEntry.include:
                if m3uEntry.type == TypeEnum.Series:
                    self.num_series_skipped += 1
                if m3uEntry.type == TypeEnum.Movie:
                    self.num_movies_skipped += 1
                if m3uEntry.type == TypeEnum.Other:
                    self.num_other_skipped += 1

                return

            output_path = utils.get_outputpath() #xbmcvfs.translatePath(f"special://home/{ADDON.getAddonInfo('id')}/{provider}")

            if m3uEntry.type == TypeEnum.Series:
                output_path = os.path.join(output_path, f'{m3uEntry.type.value}/{m3uEntry.title}/{m3uEntry.subfolder}')
            elif m3uEntry.type == TypeEnum.Movie:
                output_path = os.path.join(output_path, f'{m3uEntry.type.value}/{m3uEntry.filename}')
            else:
                return
            
            output_strm = os.path.join(output_path, m3uEntry.filename)

            if self.preview:
                return

            if not xbmcvfs.exists(output_strm):
                if not xbmcvfs.exists(output_path):
                    xbmcvfs.mkdir(output_path)

                try:
                    with open(output_strm, 'w', encoding='utf-8') as f:
                        f.write(m3uEntry.url)

                        if m3uEntry.type == TypeEnum.Series:
                            self.num_new_series += 1
                        elif m3uEntry.type == TypeEnum.Movie:
                            self.num_new_movies += 1

                        return
                except Exception as e:
                    LogManagement.error(e.with_traceback)
                    self.num_errors += 1
            else:
                self.num_movies_skipped += 1
            
            dialog.update(percent=progress, message=m3uEntry.title)

        dialog.close

    def get_extinf_urls(self, fileName):
        if not xbmcvfs.exists(fileName):
            return {}

        extinf_url_extinf_pattern = re.compile(r'#EXTINF:-1\s+(.*?)\n(http[s]?://\S+)')

        contents = self.open_file_with_progress(fileName)

        matches = extinf_url_extinf_pattern.findall(contents)
        extinf_url_dict = {}
        count = 0

        for match in matches:
            extinf = match[0]
            extinf_url = match[1]
            extinf_url_dict[extinf_url] = extinf

        return(extinf_url_dict)

    def open_file_with_progress(self, file_path):
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
     
    def diffs(self, current_playlist_path, new_playlist_path):
        currentM3uDict = self.get_extinf_urls(current_playlist_path)
        newM3uDict = self.get_extinf_urls(new_playlist_path)

        keys1 = set(currentM3uDict.keys())
        keys2 = set(newM3uDict.keys())
        diff_keys1 = keys1 - keys2
        diff_keys2 = keys2 - keys1

        diff_items1 = {k: currentM3uDict[k] for k in diff_keys1}
        diff_items2 = {k: newM3uDict[k] for k in diff_keys2}

        result = {**diff_items1, **diff_items2}

        return(result)