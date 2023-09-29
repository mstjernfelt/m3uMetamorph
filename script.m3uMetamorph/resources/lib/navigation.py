# -*- coding: utf-8 -*-

import re
import sys

import xbmc
import json
import xbmcgui

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
    headings.append(Utils.translate(30001))
    handlers.append(lambda: refresh_from_m3u())

    # Refresh from playlist (Clean run)
    headings.append(Utils.translate(30002))
    handlers.append(lambda: refresh_from_m3u(cleanrun=True))

    # Refresh from playlist (Clean run)
    headings.append("Edit groups")
    handlers.append(lambda: edit_groups())

    # Refresh from playlist (Clean run)
    headings.append("Edit TV groups")
    handlers.append(lambda: edit_tv_groups())

    # Refresh from playlist (Clean run)
    headings.append("Update Library")
    handlers.append(lambda: update_library())

    # Open Settings
    headings.append(Utils.translate(30011))
    handlers.append(Utils.open_settings)

    # Open Settings
    headings.append("Test XML TV Parser")
    handlers.append(lambda: xml_tv_parser_tester())

    # Test - For debug only
    # headings.append("Test Exception")
    # handlers.append(test_exception)

    return headings, handlers

def xml_tv_parser_tester():
    xml_tv_parser = XmlTv_Parser()

def update_library():
    xbmc.executebuiltin(function="UpdateLibrary(video)")

def edit_groups():
    groups = Groups()
    dialog = xbmcgui.Dialog()

    preselected_indices = [index for index, group in enumerate(groups.media_group_data['groups']) if group['include']]

    selected_indices = dialog.multiselect("Select Media Groups", groups.media_group_names, preselect=preselected_indices)

    if selected_indices is None:
        return

    for index, group in enumerate(groups.media_group_data['groups']):
        if index in selected_indices:
            group['include'] = True
        else:
            group['include'] = False

    # groups.existingGroupData = {**groups.media_group_data, **groups.tv_group_data}

    # with open(Utils.get_group_json_path(), 'w+') as f:
    #     json.dump(groups.existingGroupData, f, indent=4)

def edit_tv_groups():
    groups = Groups()
    dialog = xbmcgui.Dialog()

    LogManagement.info(f'groups.tv_group_data: {groups.tv_group_data["groups"]}')

    preselected_indices = [index for index, group in enumerate(groups.tv_group_data['groups']) if group['include']]

    selected_indices = dialog.multiselect("Select TV Groups", groups.tv_group_names, preselect=preselected_indices)

    if selected_indices is None:
        return

    for index, group in enumerate(groups.existingGroupData['groups']):
        if index in selected_indices:
            group['include'] = True
        else:
            group['include'] = False

    groups.existingGroupData = {**groups.media_group_data, **groups.tv_group_data}

    # with open(Utils.get_group_json_path(), 'w+') as f:
    #     json.dump(groups.existingGroupData, f, indent=4)

    for entry in groups.existingGroupData["groups"]:
        LogManagement.info(entry)

def refresh_from_m3u(cleanrun = False, generate_groups = True, preview = False):
    LogManagement.info(f'Media output Path has been set to {Utils.get_movie_output_path()}.')
    LogManagement.info(f'Playlist URL has been set to {Utils.get_playlist_url}.')
    LogManagement.info(f'IPTV Provider has been set to {Utils.get_provider_name()}.')
    LogManagement.info(f'Generate Groups has been set to {generate_groups}.')
    LogManagement.info(f'Preview mode has been set to {preview}.')

    m3uParse = M3UParser(generate_groups=generate_groups, preview=preview, cleanrun=cleanrun)

    m3uParse.parse()
    m3uParse.create_strm()
    m3uParse.generate_tv_m3u_file()

    xml_tv_parser = XmlTv_Parser(m3uParse.tv_m3u_entries)

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

    update_library = Utils.get_setting("update_library")

    if update_library:
        xbmc.executebuiltin(function="UpdateLibrary(video)", wait=False)

from resources.lib.treeview import TreeView, TreeNode
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
