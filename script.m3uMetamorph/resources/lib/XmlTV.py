import re
import os
import json
import xbmcgui
import xbmcvfs
import difflib
import xml.etree.ElementTree as ET

from enum import Enum
from typing import List
from resources.lib.FileManagement import m3uFileHandler
from resources.lib.GroupManagement import Groups
from resources.lib import LogManagement
from resources.lib import Utils
from resources.lib.M3uManagement import ExtM3U_Entry

class XmlTv_Parser:
    cleanrun: bool = False
    _xml_tv_data = None
    _groups = Groups

    def __init__(self, tv_m3u_entries: ExtM3U_Entry):
        self._groups = Groups()

        m3u_file_handler = m3uFileHandler()
        self._xml_tv_data = m3u_file_handler.get_xmltv_file()

        self.parse_xml_tv(tv_m3u_entries)

    def parse_xml_tv(self, tv_m3u_entries: [ExtM3U_Entry]):
        # Load the existing XML file
        xml_file_path = Utils.get_xmltv_url()

        #tv_entries = [entry for entry in tv_m3u_entries]
        tv_entries = []
        for entry in tv_m3u_entries:
            if entry.id != "":
                tv_entries.append(entry.id)

        tree = ET.parse(Utils.get_xmltv_path())
        root = tree.getroot()

        # Update channel elements and remove unwanted channels
        dialog = xbmcgui.DialogProgress()
        dialog.create(heading="Parsing xmltv (Channels)")
        count = 0

        channels = root.findall('.//channel')
        total = len(channels)

        for channel_elem in channels:
            count += 1
            progress = count * 100 // total
            dialog.update(percent=progress)

            channel_id = channel_elem.get('id')

            if not channel_id in tv_entries:
                # Remove the channel element if it's not in the dictionary
                root.remove(channel_elem)

            dialog.update(percent=progress, message=channel_id)

        dialog.close

        # Update programme elements
        dialog.create(heading="Parsing xmltv (Programme's)")
        count = 0

        programmes = root.findall('.//programme')
        total = len(programmes)

        for programme_elem in programmes:
            count += 1
            progress = count * 100 // total
            dialog.update(percent=progress)

            programme_channel = programme_elem.get('channel')

            if not programme_channel in tv_entries:
                # Remove the channel element if it's not in the dictionary
                root.remove(programme_elem)
            
            dialog.update(percent=progress, message=programme_channel)

        dialog.close

        # Write the modified XML to a new file
        #new_xml_file_path = "C:\\BrightCom\\GitHub\\mstjernfelt\\m3uMetamorph\\local\\new.xml"
        new_xml_file_path = Utils.get_xmltv_path()
        tree.write(new_xml_file_path, encoding='utf-8')
        LogManagement.info(f'New XML File Path: {new_xml_file_path}')

