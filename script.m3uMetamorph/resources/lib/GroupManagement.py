import json
import re
from typing import List
import xbmcvfs
import xbmcgui

from resources.lib import LogManagement
from resources.lib import Utils

class Groups:
    existingGroupData = ''
    provider = ''
    num_groups = 0
    num_provider_groups = 0

    _group_names = []
    _movie_group_names = []
    _series_group_names = []
    _media_group_names = []
    _tv_group_names = []

    class Group():
        _name: str = ""
        _include: bool = False
        _type: str = ""

        @property
        def name(self):
            return self._name
        
        @name.setter
        def name(self, value: str):
            self._name = value

        @property
        def include(self):
            return self._name
        
        @include.setter
        def include(self, value: bool):
            self._include = value
            
        @property            
        def type(self):
            return self._type
        
        @type.setter
        def type(self, value: str):
            self._type = value

    @property
    def media_group_data(self):
        # Create a dictionary to store filtered entries
        filtered_entries = []

        # Define the regex pattern
        movie_include_pattern = re.escape(Utils.get_setting("movie_include"))
        series_include_pattern = re.escape(Utils.get_setting("series_include"))
        re_pattern = re.compile(f'{movie_include_pattern}|{series_include_pattern}')

        # Iterate through the entries and filter based on the pattern and 'include' key
        for group in self.existingGroupData['groups']:
            if re.match(re_pattern, group['name']):
                filtered_entries.append(group)  # Use 'name' as the key

        filtered_entries = { 'groups': filtered_entries }

        return filtered_entries     
    
    @property
    def tv_group_data(self):
        # Create a dictionary to store filtered entries
        filtered_entries = []

        # Define the regex pattern
        movie_include_pattern = re.escape(Utils.get_setting("movie_include"))
        series_include_pattern = re.escape(Utils.get_setting("series_include"))
        re_pattern = re.compile(f'^(?!.*(?:{movie_include_pattern}|{series_include_pattern})).*$')

        # Iterate through the entries and filter based on the pattern and 'include' key
        for group in self.existingGroupData['groups']:
            if re.match(re_pattern, group['name']):
                filtered_entries.append(group)  # Use 'name' as the key

        tv_group_data = { 'groups': filtered_entries }

        return tv_group_data

    @property
    def group_names(self) -> []:
        self._group_names = [group['name'] for group in self.existingGroupData['groups']]

        return self._group_names

    @property
    def movie_group_names(self) -> []:
        re_pattern = re.compile(Utils.get_setting('movie_include'))

        self._movie_group_names = self._filter_entries_with_regex(self.group_names, re_pattern)

        return self._movie_group_names

    @property
    def series_group_names(self) -> []:
        re_pattern = re.compile(Utils.get_setting('series_include'))

        self._series_group_names = self._filter_entries_with_regex(self.group_names, re_pattern)

        return self._series_group_names

    @property
    def media_group_names(self) -> []:
        re_pattern = re.compile(f'{Utils.get_setting("series_include")}|{Utils.get_setting("movie_include")}')

        self._media_group_names = self._filter_entries_with_regex(self.group_names, re_pattern)

        return self._media_group_names

    @property
    def tv_group_names(self) -> []:
        re_pattern = re.compile(f'^(?!.*(?:{Utils.get_setting("movie_include")}|{Utils.get_setting("series_include")})).*$')

        self._tv_group_names = self._filter_entries_with_regex(self.group_names, re_pattern)

        return self._tv_group_names

    @property
    def included_tv_groups(self) -> {}:
        # Create a dictionary to store filtered entries
        filtered_entries = {}

        # Define the regex pattern
        movie_include_pattern = re.escape(Utils.get_setting("movie_include"))
        series_include_pattern = re.escape(Utils.get_setting("series_include"))
        pattern = f'^(?!.*(?:{movie_include_pattern}|{series_include_pattern})).*$'

        # Iterate through the entries and filter based on the pattern and 'include' key
        for group in self.existingGroupData['groups']:
            if group['include'] and re.match(pattern, group['name']):
                filtered_entries[group['name']] = group  # Use 'name' as the key

        return filtered_entries

    def __init__(self, playlist_data = None, generate_groups = None):
        LogManagement.info(f'Group settings file path: {Utils.get_group_json_path()}.')
        #import web_pdb; web_pdb.set_trace()

        if generate_groups:
            #Load groups from playlist
            playlistGroupData = self.get_groups_from_playlist(playlist_data)

            # Load existing JSON data from file
            self.load()
            self.set(playlistGroupData)
            self.num_groups = self.save()

            self.num_provider_groups = len(playlistGroupData)

            LogManagement.info(f'{self.num_groups} groups whas added to groups.json, provider has a total of {self.num_provider_groups} groups in playlist.')
        else:
            self.load()

    def load(self):
        #import web_pdb; web_pdb.set_trace()
        existingData = ""

        if xbmcvfs.exists(Utils.get_group_json_path()):
            try:
                with xbmcvfs.File(Utils.get_group_json_path(), 'r') as f:
                    self.existingGroupData = json.load(f)

                    if len(self.existingGroupData) == 0:
                        self.existingGroupData = {'groups': []}
                        return
                    
                f.close()

            #except json.decoder.JSONDecodeError as e:
            except Exception as e:
                LogManagement.info(f'Exception: {e}')
                self.existingGroupData = {'groups': []}  # or any other default value you want to use
                return
        else:
            self.existingGroupData = {'groups': []}
            return

    def set(self, playlistGroupData):
        existing_groups = self.existingGroupData.get('groups', [])

        differences = {}

        for existing_group in existing_groups:
            existing_group_name = existing_group['name']
            existing_group_include = existing_group['include']

            for key, value in playlistGroupData.items():
                if value['name'] == existing_group_name and value['include'] != existing_group_include:
                    differences[existing_group_name] = {
                        'name': existing_group_name,
                        'include': existing_group_include
                    }
                    break

        for key, value in playlistGroupData.items():
            if not any(existing_group['name'] == value['name'] for existing_group in existing_groups):
                differences[value['name']] = {
                    'name': value['name'],
                    'include': value['include']
                }

        # Add any new groups to the list
        newGroups = 0
        for group in differences:
            if not any(existing_group['name'] == group for existing_group in existing_groups):
                newGroups += 1
                existing_groups.append({'name': group, 'include': False})

        # Convert Python data structure back to JSON format
        self.existingGroupData = {'groups': existing_groups}

    def save(self) -> int:
        # Initialize old data as an empty dictionary
        old_data = {}

        # Check if the JSON file exists
        if xbmcvfs.exists(Utils.get_group_json_path()):
            try:
                # Attempt to load existing JSON data
                with xbmcvfs.File(Utils.get_group_json_path(), 'r') as f:
                    old_data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                pass  # Handle JSON decoding error, but continue with empty old_data

        # Initialize a change count to track the number of new groups added
        new_groups = self.existingGroupData.get("groups", [])
        old_groups = old_data.get("groups", [])
        change_count = len(new_groups) - len(old_groups)

        # Update the original dictionary with the new data
        old_data["groups"] = new_groups

        # Save the updated JSON data to file
        with xbmcvfs.File(Utils.get_group_json_path(), 'w+') as f:
            json.dump(old_data, f, indent=4)

        return change_count

    def check_group_inclusion(self, groupTitle) -> bool:
        for group in self.existingGroupData.values():
            for item in group:
                itemName = item['name']

                if itemName == groupTitle:
                    if item['include'] == 'Always':
                        return True
                    
                    itemInclude = item['include']
                    return itemInclude
                
        return False

    def get_groups_from_playlist(self, m3uData):
        playlistGroupData = {}

        for line in m3uData.values():
            regExResult = re.search('group-title="([^"]+)"', line)

            if regExResult:
                groupname = regExResult.group(1)

                playlistGroupData[groupname] = {
                    "name": groupname,
                    "include": False
                }

        return playlistGroupData
    
    def _filter_entries_with_regex(self, data, pattern: re):
        filtered_list = [entry for entry in data if pattern.search(entry)]
        return filtered_list

    def edit_media_groups(self):
        self.edit_groups(self.media_group_data)

    def edit_tv_groups(self):
        self.edit_groups(self.tv_group_data)

    def edit_groups(self, group_data: List[Group]):
        groups = Groups()
        dialog = xbmcgui.Dialog()

        preselected_indices = [index for index, group in enumerate(group_data['groups']) if group['include']]

        media_groups_name = [str(group['name']) for group in group_data['groups']]

        LogManagement.info(f'media_groups_name: {media_groups_name}')

        selected_indices = dialog.multiselect("Select Media Groups", media_groups_name, preselect=preselected_indices)

        if selected_indices is None:
            return

        for index, group in enumerate(group_data['groups']):
            if index in selected_indices:
                group['include'] = True
            else:
                group['include'] = False

        for media_group in group_data['groups']:
            for existing_group in groups.existingGroupData['groups']:
                if media_group['name'] == existing_group['name']:
                    existing_group['include'] = media_group['include']
                    break  # Break out of the inner loop once a match is found

        with open(Utils.get_group_json_path(), 'w+') as f:
            json.dump(groups.existingGroupData, f, indent=4)    
