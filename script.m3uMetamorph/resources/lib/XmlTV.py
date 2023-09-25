import re
import os
import json
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET

from enum import Enum
from typing import List
from resources.lib.GroupManagement import Groups
from resources.lib.FileManagement import m3uFileHandler
from resources.lib import LogManagement
from resources.lib import Utils

class XmlTv_Parser:
    cleanrun: bool = False
    xml_tv_data = None

    def __init__(self, generate_groups=None, preview=False, cleanrun=False):
        self.cleanrun = cleanrun

        m3u_file_handler = m3uFileHandler()
        m3u_file_handler.get_xmltv_file(_cleanrun=self.cleanrun)

        self.xml_tv_data = m3u_file_handler.open_file_with_progress(Utils.get_xmltv_path())

        LogManagement.info(f'self.xml_tv_data before: {len(self.xml_tv_data)}')

        self._check_for_differences(m3u_file_handler.current_xmltv_path)

        LogManagement.info(f'self.xml_tv_data after: {len(self.xml_tv_data)}')

    def _check_for_differences(self, xml_tv_path):
        if self.cleanrun:
            return
        
        self.xml_tv_data = self.compare_xml_files(current_xml_tv_path=xml_tv_path, new_xml_tv_path=Utils.get_xmltv_path())

    def compare_xml_files(current_xml_tv_path, new_xml_tv_path):
        try:
            # Parse both XML files
            tree1 = ET.parse(current_xml_tv_path)
            tree2 = ET.parse(new_xml_tv_path)

            # Get the root elements of both trees
            root1 = tree1.getroot()
            root2 = tree2.getroot()

            # Compare the XML trees
            differences = []

            # Define a recursive function to compare elements and their attributes
            def compare_elements(elem1, elem2):
                if elem1.tag != elem2.tag:
                    differences.append(f"Element name mismatch: {elem1.tag} != {elem2.tag}")

                if elem1.text != elem2.text:
                    differences.append(f"Text content mismatch: {elem1.text} != {elem2.text}")

                if elem1.attrib != elem2.attrib:
                    differences.append(f"Attribute mismatch in element '{elem1.tag}': {elem1.attrib} != {elem2.attrib}")

                for child1, child2 in zip(elem1, elem2):
                    compare_elements(child1, child2)

            compare_elements(root1, root2)

            return differences
        except Exception as e:
            print("An error occurred:", str(e))
            return None

    # Example usage:
    # file1_path = "path/to/your/file1.xml"
    # file2_path = "path/to/your/file2.xml"
    # differences = compare_xml_files(file1_path, file2_path)
    # if differences:
    #     for diff in differences:
    #         print(diff)
    # else:
    #     print("No differences found.")