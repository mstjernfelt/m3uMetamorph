# -*- coding: utf-8 -*-

import sys

import xbmc
import json
import xbmcgui

from resources.lib import logviewer
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
    headings.append("Update Library")
    handlers.append(lambda: update_library())

    # Open Settings
    headings.append(Utils.translate(30011))
    handlers.append(Utils.open_settings)

    # Open Settings
    headings.append("Dispaly Tree View")
    handlers.append(lambda: display_tree())

    # Test - For debug only
    # headings.append("Test Exception")
    # handlers.append(test_exception)

    return headings, handlers

def update_library():
    xbmc.executebuiltin(function="UpdateLibrary(video)")

def edit_groups():
    # Create a Kodi dialog
    dialog = xbmcgui.Dialog()

    # Create a list to store the edited data
    groups = Groups()

    # Parse JSON data into a dictionary
    data = groups.existingGroupData

    # Create a Kodi dialog
    dialog = xbmcgui.Dialog()

    # Create a list of group names for the multiselect dialog
    group_names = [group['name'] for group in data['groups']]

    # Create a list of preselected indices based on 'include' value
    preselected_indices = [index for index, group in enumerate(data['groups']) if group['include']]

    # Show the multiselect dialog
    selected_indices = dialog.multiselect("Select Groups", group_names, preselect=preselected_indices)

    if selected_indices is None:
        return

    # Update the 'include' value for the selected groups
    for index, group in enumerate(data['groups']):
        if index in selected_indices:
            group['include'] = True
        else:
            group['include'] = False

    #import web_pdb; web_pdb.set_trace()

    # Convert the updated dictionary back to JSON
    with open(Utils.get_group_json_path(), 'w+') as f:
        json.dump(data, f, indent=4)

    # Now, `updated_json_data` contains the edited JSON data


def refresh_from_m3u(cleanrun = False, generate_groups = True, preview = False):
    LogManagement.info(f'Media output Path has been set to {Utils.get_movie_output_path()}.')
    LogManagement.info(f'Playlist URL has been set to {Utils.get_playlist_url}.')
    LogManagement.info(f'IPTV Provider has been set to {Utils.get_provider_name()}.')
    LogManagement.info(f'Generate Groups has been set to {generate_groups}.')
    LogManagement.info(f'Preview mode has been set to {preview}.')

    m3uParse = M3UParser(generate_groups=generate_groups, preview=preview, cleanrun=cleanrun)

    m3uParse.parse()
    m3uParse.create_strm()
    m3uParse.generate_extm3u_other_file()

    xml_tv_parser = XmlTv_Parser(generate_groups=generate_groups, preview=preview, cleanrun=cleanrun)

    m3uParse.dumpjson(m3uParse.m3u_entries, "C:\kodi\Output\MonsterIPTV\m3u_entries.json")
    m3uParse.dumpjson(m3uParse.m3u_entries_other, "C:\kodi\Output\MonsterIPTV\m3u_entries_other.json")

    # Your messages
    messages = [
        "Finished parsing m3u playlist",
        f'{m3uParse.num_new_movies} new movies were added',
        f'{m3uParse.num_new_series} new tv show episodes were added',
        f'{m3uParse.groups.num_groups} new groups where added to group setup\n',
        f'{m3uParse.num_movies_skipped} movies skipped due to group setup',
        f'{m3uParse.num_series_skipped} series skipped due to group setup',
        f'{m3uParse.num_movies_exists} movie/s in playlist already exist',
        f'{m3uParse.num_series_exists} serie/s in playlist already exist\n',
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

def show_log(old):
    content = logviewer.get_content(old, Utils.get_inverted(), Utils.get_lines(), True)
    logviewer.window(Utils.ADDON_NAME, content, default=Utils.is_default_window())

def run():
    if len(sys.argv) > 1:
        # Integration patterns below:
        # Eg: xbmc.executebuiltin("RunScript(script.logviewer, show_log)")
        method = sys.argv[1]

        if method == "show_log":
            show_log(False)
        elif method == "show_old_log":
            show_log(True)
        else:
            raise NotImplementedError("Method '{}' does not exist".format(method))
    else:
        headings, handlers = get_opts()
        index = xbmcgui.Dialog().select(Utils.ADDON_NAME, headings)

        if index >= 0:
            handlers[index]()
