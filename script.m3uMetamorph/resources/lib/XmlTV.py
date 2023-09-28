import re
import os
import json
import xbmcgui
import xbmcvfs
import difflib
import xml.etree.ElementTree as ET

from enum import Enum
from typing import List
from resources.lib.GroupManagement import Groups
from resources.lib.FileManagement import m3uFileHandler
from resources.lib import LogManagement
from resources.lib import Utils

class XmlTv_Parser:
    cleanrun: bool = False
    new_xml_tv_data = None
    current_xml_tv_data = None

    def __init__(self, generate_groups=None, preview=False, cleanrun=False):
        self.cleanrun = cleanrun

        m3u_file_handler = m3uFileHandler()
        m3u_file_handler.get_xmltv_file(_cleanrun=self.cleanrun)

        LogManagement.info(f'self.xml_tv_data before: {self.xml_tv_data}')

        if not self.cleanrun and os.path.exists(Utils.get_xmltv_path()):
            self.xml_tv_data = self._compare_identical_xml_files(m3u_file_handler.current_xmltv_path, Utils.get_xmltv_path())

        LogManagement.info(f'self.xml_tv_data after: {self.xml_tv_data}')

    def _compare_identical_xml_files(self, current_xml_tv_path, new_xml_tv_path):
        currentM3uDict = self._get_extinf_urls(current_xml_tv_path)
        newM3uDict = self._get_extinf_urls(new_xml_tv_path)

        keys1 = set(currentM3uDict.keys())
        keys2 = set(newM3uDict.keys())
        diff_keys1 = keys1 - keys2
        diff_keys2 = keys2 - keys1

        diff_items1 = {k: currentM3uDict[k] for k in diff_keys1}
        diff_items2 = {k: newM3uDict[k] for k in diff_keys2}

        result = {**diff_items1, **diff_items2}

        return(result)

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
