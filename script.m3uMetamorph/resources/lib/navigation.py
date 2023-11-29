# -*- coding: utf-8 -*-

import re
import sys
from typing import List

import xbmc
import json
import xbmcgui

from resources.lib.treeview import TreeView, TreeNode
from resources.lib import Utils
from resources.lib import LogManagement
from resources.lib.M3uManagement import M3UParser
from resources.lib.GroupManagement import Groups
from resources.lib.XmlTV import XmlTv_Parser

def has_addon(addon_id):
    return xbmc.getCondVisibility("System.HasAddon({})".format(addon_id)) == 1

def test_exception():
    import random
    raise Exception(str(random.randint(0, 1000)))

def get_opts():
    headings = []
    handlers = []

    # Refresh from playlist (Incremental)
    headings.append('Incremental run')
    handlers.append(lambda: refresh_from_m3u())

    # Refresh from playlist (Incremental)
    headings.append('Incremental run (Preview)')
    handlers.append(lambda: refresh_from_m3u(preview=True))

    # Refresh from playlist (Clean run)
    headings.append('Clean run')
    handlers.append(lambda: refresh_from_m3u(cleanrun=True))

    # Refresh from playlist (Clean run)
    headings.append('Clean run (Preview, Generate Groups)')
    handlers.append(lambda: refresh_from_m3u(cleanrun=True, preview=True))

    # Refresh from playlist (Clean run)
    headings.append("Edit groups")
    groups = Groups()
    handlers.append(lambda: groups.edit_media_groups())

    # Refresh from playlist (Clean run)
    headings.append("Edit TV groups")
    groups = Groups()
    handlers.append(lambda: groups.edit_tv_groups())

    # Refresh from playlist (Clean run)
    headings.append("Update Library")
    handlers.append(lambda: update_library())

    # Open Settings
    headings.append(Utils.translate(30011))
    handlers.append(Utils.open_settings)

    # Open Settings
    headings.append("select_group_outputpath")
    handlers.append(lambda: select_group_outputpath())

    # Test - For debug only
    # headings.append("Test Exception")
    # handlers.append(test_exception)

    return headings, handlers

def xml_tv_parser_tester():
    xml_tv_parser = XmlTv_Parser()

def update_library():
    xbmc.executebuiltin(function="UpdateLibrary(video)")

def refresh_from_m3u(cleanrun = False, generate_groups = True, preview = False):
    LogManagement.info(f'Media output Path has been set to {Utils.get_movie_output_path()}.')
    LogManagement.info(f'Playlist URL has been set to {Utils.get_playlist_url()}.')
    LogManagement.info(f'Generate Groups has been set to {generate_groups}.')
    LogManagement.info(f'Clean run has been set to {cleanrun}.')
    LogManagement.info(f'Preview mode has been set to {preview}.')

    m3uParse = M3UParser(generate_groups=generate_groups, preview=preview, cleanrun=cleanrun)

    m3uParse.parse()
    m3uParse.create_strm()
    m3uParse.generate_tv_m3u_file()

    #xml_tv_parser = XmlTv_Parser(m3uParse.tv_m3u_entries)

    m3uParse.dumpjson(m3uParse.m3u_entries, "C:\BrightCom\GitHub\mstjernfelt\m3uMetamorph\local\m3u_entries.json")
    m3uParse.dumpjson(m3uParse.tv_m3u_entries, "C:\BrightCom\GitHub\mstjernfelt\m3uMetamorph\local\\tv_m3u_entries.json")

    # Your messages
    messages = [
        "Finished parsing m3u playlist",
        f'{m3uParse.num_new_movies} new movies were added',
        f'{m3uParse.num_new_series} new tv show episodes were added',
        f'{m3uParse.groups.num_groups} new groups where added to group setup',
        f'{m3uParse.num_movies_skipped} movies skipped due to group setup',
        f'{m3uParse.num_series_skipped} series skipped due to group setup',
        f'{m3uParse.num_movies_exists} movie/s in playlist already exist',
        f'{m3uParse.num_series_exists} serie/s in playlist already exist',
        f'{m3uParse.num_errors} errors writing strm file/s',
    ]

    for message in messages:
        LogManagement.info(message)

    # Concatenate the messages into one string
    message_text = "\n".join(messages)

    # Display the messages in a dialog
    dialog = xbmcgui.Dialog()
    dialog.textviewer("Parsing result", message_text)

    # update_library = Utils.get_setting("update_library")

    # if update_library:
    #     xbmc.executebuiltin(function="UpdateLibrary(video)", wait=False)

import xbmcgui

def select_group_outputpath():
    # Load the JSON data
    with open('C:\BrightCom\GitHub\mstjernfelt\m3uMetamorph\local\groups_path.json', 'r') as data_file:
        group_data = json.load(data_file)

    # Create a list of group names
    group_names = [group['name'] for group in group_data['groups']]

    # Show a dialog to select a group
    selected_group_index = xbmcgui.Dialog().select('Select a group', group_names)

    if selected_group_index >= 0:
        # Get the selected group and its current output path
        selected_group = group_data['groups'][selected_group_index]

        # Create a list of setting items for the settings dialog
        setting_items = [
            ('Group Name', selected_group['name']),
            ('Current Output Path', selected_group['output path'])
        ]

        # Create a settings dialog
        dialog = xbmcgui.Dialog()
        #dialog.setHeading('Group Settings')
        selected_setting_index = dialog.settings(setting_items)

        # Handle the user's selection
        if selected_setting_index >= 0:
            # Update the selected group's output path with the new value
            new_output_path = setting_items[1][1]  # Index 1 corresponds to the output path
            selected_group['output path'] = new_output_path

            # Save the updated JSON data
            with open('C:\BrightCom\GitHub\mstjernfelt\m3uMetamorph\local\groups_path.json', 'w') as data_file:
                json.dump(group_data, data_file, indent=4)

            xbmcgui.Dialog().ok('Settings Updated', 'Output path updated successfully.')
        else:
            xbmcgui.Dialog().ok('Cancelled', 'You cancelled the settings dialog')

def display_tree():
    # Create a sample hierarchical data structure
    root_node = TreeNode("Root", [
        TreeNode("Item 1", [
            TreeNode("Subitem 1.1"),
            TreeNode("Subitem 1.2"),
        ]),
        TreeNode("Item 2", [
            TreeNode("Subitem 2.1"),
        ]),
    ])

    # Create a TreeView instance
    tree_view = TreeView(root_node)

    # Display the tree view
    tree_view.display_tree()

def run():
    if len(sys.argv) > 1:
        # Integration patterns below:
        # Eg: xbmc.executebuiltin("RunScript(script.logviewer, show_log)")
        method = sys.argv[1]
    else:
        headings, handlers = get_opts()
        index = xbmcgui.Dialog().select(Utils.ADDON_NAME, headings)

        if index >= 0:
            handlers[index]()
