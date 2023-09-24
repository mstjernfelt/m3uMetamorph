import json
import re
import xbmc
import xbmcvfs

from resources.lib import LogManagement
from resources.lib import utils

class Groups:
    existingGroupData = ''
    provider = ''
    num_groups = 0
    num_provider_groups = 0

    def __init__(self, playlist_data = None, generate_groups = None):
        LogManagement.info(f'Group settings file path: {utils.get_group_json_path()}.')
        #import web_pdb; web_pdb.set_trace()

        if generate_groups:
            #Load groups from playlist
            LogManagement.info(f'Found {len(playlist_data)} entries to get groups from.')

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

        if xbmcvfs.exists(utils.get_group_json_path()):
            try:
                with xbmcvfs.File(utils.get_group_json_path(), 'r') as f:
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
        if xbmcvfs.exists(utils.get_group_json_path()):
            try:
                with xbmcvfs.File(utils.get_group_json_path(), 'r') as f:
                     old_data = json.load(f)
            except json.decoder.JSONDecodeError as e:
                old_data = {}
        else:
            old_data = {}

        newGroupData = {}

        # Update the original dictionary with the new data
        if len(newGroupData) > 0:
            self.existingGroupData = newGroupData

        # Save the updated JSON data to file
        with xbmcvfs.File(utils.get_group_json_path(), 'w+') as f:
             json.dump(self.existingGroupData, f, indent=4)

        with xbmcvfs.File(utils.get_group_json_path(), 'r') as f:
            old_data = json.load(f)

        oldDataCount = 0
        newDataCount = 0
        if 'groups' in old_data:
            oldDataCount = len(old_data["groups"])
        
        if 'groups' in self.existingGroupData:
            newDataCount = len(self.existingGroupData['groups'])

        return(newDataCount - oldDataCount)

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