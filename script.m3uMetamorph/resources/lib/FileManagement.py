import urllib.request
import tempfile
import re

import xbmcvfs
import xbmcgui
import xbmc

from resources.lib import LogManagement
from resources.lib import utils

class m3uFileHandler():

    current_playlist_path = ""
    logger = None
    # Create a progress dialog
    dialog = xbmcgui.DialogProgress()

    def get_m3u_file(self, _cleanrun=False) -> str:
        # Check if the URL is a local file path or a remote URL
        LogManagement.info(f'Loading playlist from {utils.get_playlist_url()}.')

        # Use the addon_path as needed
        LogManagement.info(f'Playlist save path: {utils.get_playlist_path()}.')

        if _cleanrun:
            if xbmcvfs.exists(utils.get_playlist_path()):
                # Delete the file
                xbmcvfs.delete(utils.get_playlist_path())

                LogManagement.info(f"cleanrun was set, the file {utils.get_playlist_path()} has been deleted.")
            else:
                LogManagement.info(f"cleanrun was set, The file {utils.get_playlist_path()} does not exist.")

        # Get the temporary directory path
        temp_dir = xbmcvfs.translatePath('special://home/')            
        temp_file_path = tempfile.mktemp(dir=temp_dir)

        if xbmcvfs.exists(utils.get_playlist_path()):
            LogManagement.info(f"m3u file exists: {utils.get_playlist_path()}")
            # create a temporary file

            # Generate a unique name for the temporary file
            LogManagement.info(f"Created temp file {temp_file_path}")

            #temp_file = xbmcvfs.File(temp_file_path, 'w')

            # get the path of the temporary file
            self.current_playlist_path = temp_file_path

            # use shutil.copy() to copy the contents of the source file to the temporary file
            LogManagement.info(f"Copy current playlist ({utils.get_playlist_path()}) to temp ({self.current_playlist_path})")

            xbmcvfs.copy(utils.get_playlist_path(), self.current_playlist_path)

        if utils.get_playlist_url().startswith('http') or utils.get_playlist_url().startswith('https'):
            if not xbmcvfs.exists(utils.get_outputpath()):
                xbmcvfs.mkdirs(utils.get_outputpath())

            # Set the properties of the progress dialog
            self.dialog.create('Task Progress', f"Downloading playlist...")

            # Start the task in a separate thread or process
            # In this example, we execute the task in the main thread for simplicity

            try:           
                urllib.request.urlretrieve(utils.get_playlist_url(), temp_file_path, reporthook = self.progress_callback)

                playlist_path = utils.get_playlist_path()
                result = xbmcvfs.copy(temp_file_path, playlist_path)

                if not result:
                    LogManagement.error(f'Error copying playlist to {playlist_path}')    
            except:
                xbmcvfs.delete(temp_file_path)

            # Close the progress dialog
            self.dialog.close()

            LogManagement.info(f'Playlist downloaded to {utils.get_playlist_path()}')
        else:
            xbmcvfs.copy(utils.get_playlist_url(), utils.get_playlist_path())

            LogManagement.info(f'Playlist copied to {utils.get_playlist_path()}')

        LogManagement.info(f'Loaded playlist successfully.')

    def progress_callback(self, count, block_size, total_size):
        # Calculate the download percentage
        progress = count * block_size * 100 // total_size

        self.dialog.update(progress)

    def cleanup_filename(filename) -> str:
        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"

        new_string = re.sub(pattern, "", filename)

        return(new_string)