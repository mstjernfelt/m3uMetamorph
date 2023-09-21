import re
from resources.lib.GroupManagement import Groups
from resources.lib.FileManagement import m3uFileHandler
from resources.lib import LogManagement
from resources.lib import utils

import os
import xbmcgui
import xbmcvfs

class m3uParser:
    groups = None
    logger = None
    provider = None
    m3u_Url = None
    playlist_data_diff = None
    preview = False
    playListData = None

    num_titles_skipped = 0
    num_new_series = 0
    num_new_movies = 0
    num_errors = 0
    num_not_in_moviedatabase = 0

    def __init__(self, in_generate_groups = None, in_preview=False, in_cleanrun=False):

        self.preview = in_preview

        file_management = m3uFileHandler()
        file_management.get_m3u_file(in_cleanrun=in_cleanrun)

        
        #import web_pdb; web_pdb.set_trace()
        self.playListData = self.open_file_with_progress(utils.get_playlist_path())

        self.playlist_data_diff = self.Check_For_Differences(file_management.playlist_temp_path, in_cleanrun = False)

        self.groups = Groups(generate_groups = in_generate_groups, playlist_data=self.playlist_data_diff)
        
    def Check_For_Differences(self, playlist_temp_path, in_cleanrun):
        if in_cleanrun:
            return

        LogManagement.info(f'Working out differences since last run.')

        playlist_data = self.diffs(playlist_temp_path, utils.get_playlist_path())
        
        LogManagement.info(f'Found {len(playlist_data)} differences to process.')

        return playlist_data

    def parse(self):
        #import web_pdb; web_pdb.set_trace()

        dialog = xbmcgui.DialogProgress()
        dialog.create(heading= "Processing playlist titles")

        count = 0

        for url, line in self.playlist_data_diff.items():
            count += 1
            progress = count * 100 // len(self.playlist_data_diff.items())
            dialog.update(percent=progress)

            if not self.check_title_include(line):
                 self.num_titles_skipped += 1
                 continue
            else:
                 include_from_title_check = True

            tvgname = re.search('tvg-name="([^"]+)"', line)

            if tvgname and 'tvg-name' in tvgname.group(0):

                if '[Series]' in line or 'Series:' in line:
                    titleType = 'Series'
                elif '[VOD]' in line or 'VOD:' in line or '(VOD)' in line:
                    titleType = 'Movies'
                else:
                    LogManagement.info(f'TitleType: Line {line} was skipped')
                    continue

                tvgname = tvgname.group(1)
                tvgname = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', tvgname)
                
                if titleType == 'Series':
                    title = self.get_title_from_tvgname(tvgname)
                    subfolder = self.get_subfolder_from_tvgname(tvgname)
                    filename = self.get_filename_from_tvgname(tvgname)

                    # include_from_the_movie_db = the_movie_db.search(title, tvshows_to_include)

                    # if not include_from_the_movie_db or not include_from_title_check:
                    if not include_from_title_check:
                        self.num_not_in_moviedatabase += 1
                        continue
                else:
                    sub = re.sub(r"\[(?!\d{4}\])[^]]*\]", "", tvgname)
                    filename = sub
                    subfolder = sub
                    title = sub
                    
                    # include_from_the_movie_db = the_movie_db.search(title, movies_to_include)
                    
                    # if include_from_the_movie_db and include_from_title_check:
                    if not include_from_title_check:
                        self.num_not_in_moviedatabase += 1
                        continue

                dialog.update(percent=progress, message=title)

                params = {'filename': filename, 'title': title, 'titleType': titleType, 'sub_folder': subfolder, 'url': url}

                self.create_strm(params)

        LogManagement.info("Finished parsing m3u playlist")
        LogManagement.info(f"{self.num_titles_skipped} titles skipped")
        LogManagement.info(f"{self.num_new_movies} new movies were added")
        LogManagement.info(f"{self.num_new_series} new tv show episodes were added")
        LogManagement.info(f"{self.num_errors} errors writing strm file/s")

        dialog.close
        LogManagement.info("Parsing is done!")                      

    def create_strm(self,params):
        global share_user_name
        global share_password

        output_path = utils.get_outputpath() #xbmcvfs.translatePath(f"special://home/{ADDON.getAddonInfo('id')}/{provider}")
        LogManagement.info(f"Output path is set to {output_path}")

        titleType = params['titleType']
        titleType = m3uFileHandler.cleanup_filename(titleType)

        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', params['filename'])
        filename = m3uFileHandler.cleanup_filename(filename)

        title = params['title']
        title = m3uFileHandler.cleanup_filename(title)

        sub_folder = params['sub_folder']
        sub_folder = m3uFileHandler.cleanup_filename(sub_folder)

        if titleType == 'Series':
            output_path = os.path.join(output_path, f'{titleType}/{title}/{sub_folder}')
        else:
            output_path = os.path.join(output_path, f'{titleType}/{filename}')

        output_strm = os.path.join(output_path, filename + '.strm')

        if self.preview:
            return

        #import web_pdb; web_pdb.set_trace()
        utils.debug_breakpont()

        if not xbmcvfs.exists(output_strm):
            if not xbmcvfs.exists(output_path):
                xbmcvfs.mkdir(output_path)

            try:
                with open(output_strm, 'w', encoding='utf-8') as f:
                    f.write(params['url'])

                    if titleType == 'Series':
                        self.num_new_series += 1
                    elif titleType == 'Movies':
                        self.num_new_movies += 1

                    return
            except Exception as e:
                LogManagement.error(e.with_traceback)
                self.num_errors += 1                

    def get_title_from_tvgname(self, tvgname):
        pattern = r'^(.*?) S\d+'
        match = re.search(pattern, tvgname)

        if match:
            title = match[1]
        else:
            return('')
        
        return(title)

    def get_subfolder_from_tvgname(self, tvgname):
        pattern = r'^(.*?)\bS\d{1,2}'
        match = re.match(pattern, tvgname)

        if match:
            subfolder = match[0]
        else:
            return('')
        
        return(subfolder)

    def get_filename_from_tvgname(self, tvgname):
        pattern = r'^.*S\d{2}\s+(.*)$'
        match = re.search(pattern, tvgname)

        if match:
            filename = match[1]
        else:
            return('')
        
        return(filename)

    def check_title_include(self, line):
        tvgIdMatch = re.search('tvg-id=""', line)
        
        if not tvgIdMatch:
            self.num_titles_skipped += 1
            return(False)

        grouptitleMatch = re.search('group-title="([^"]+)"', line)
        if grouptitleMatch is None:
            self.num_titles_skipped += 1
            return(False)

        if not self.groups.include(grouptitleMatch.group(1)):
            self.num_titles_skipped += 1
            return(False)
        else:
            return(True)

    def get_urls(self, fileName):
        if not xbmcvfs.exists(fileName):
            return {}

        url_extinf_pattern = re.compile(r'#EXTINF:-1\s+(.*?)\n(http[s]?://\S+)')

        contents = self.open_file_with_progress(fileName)

        matches = url_extinf_pattern.findall(contents)
        url_dict = {}
        count = 0

        for match in matches:
            count+=1
            progress = count * 100 // len(matches)

            extinf = match[0]
            url = match[1]
            url_dict[url] = extinf

        return(url_dict)

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
     
    def diffs(self, currentFile, newFile):
        currentM3uDict = self.get_urls(currentFile)
        newM3uDict = self.get_urls(newFile)

        keys1 = set(currentM3uDict.keys())
        keys2 = set(newM3uDict.keys())
        diff_keys1 = keys1 - keys2
        diff_keys2 = keys2 - keys1

        diff_items1 = {k: currentM3uDict[k] for k in diff_keys1}
        diff_items2 = {k: newM3uDict[k] for k in diff_keys2}

        result = {**diff_items1, **diff_items2}

        return(result)