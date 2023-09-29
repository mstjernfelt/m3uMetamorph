import urllib.request
import tempfile
import re

import xbmcvfs
import xbmcgui
import xbmc

from resources.lib import LogManagement
from resources.lib import Utils

class m3uFileHandler():

    current_playlist_path = ""
    current_xmltv_path = ""
    logger = None
    # Create a progress dialog
    dialog = xbmcgui.DialogProgress()

    def get_m3u_file(self, _cleanrun=False) -> str:
        # Check if the URL is a local file path or a remote URL
        LogManagement.info(f'Loading playlist from {Utils.get_playlist_url()}.')

        # Use the addon_path as needed
        LogManagement.info(f'Playlist save path: {Utils.get_playlist_path()}.')

        if _cleanrun:
            if xbmcvfs.exists(Utils.get_playlist_path()):
                # Delete the file
                xbmcvfs.delete(Utils.get_playlist_path())

                LogManagement.info(f"cleanrun was set, the file {Utils.get_playlist_path()} has been deleted.")
            else:
                LogManagement.info(f"cleanrun was set, The file {Utils.get_playlist_path()} does not exist.")

        # Get the temporary directory path
        temp_dir = xbmcvfs.translatePath('special://home/')            
        temp_file_path = tempfile.mktemp(dir=temp_dir)

        if xbmcvfs.exists(Utils.get_playlist_path()):
            LogManagement.info(f"m3u file exists: {Utils.get_playlist_path()}")
            # create a temporary file

            # Generate a unique name for the temporary file
            LogManagement.info(f"Created temp file {temp_file_path}")

            #temp_file = xbmcvfs.File(temp_file_path, 'w')

            # get the path of the temporary file
            self.current_playlist_path = temp_file_path

            # use shutil.copy() to copy the contents of the source file to the temporary file
            LogManagement.info(f"Copy current playlist ({Utils.get_playlist_path()}) to temp ({self.current_playlist_path})")

            xbmcvfs.copy(Utils.get_playlist_path(), self.current_playlist_path)

        if Utils.get_playlist_url().startswith('http') or Utils.get_playlist_url().startswith('https'):
            if not xbmcvfs.exists(Utils.get_movie_output_path()):
                xbmcvfs.mkdirs(Utils.get_movie_output_path())

            # Set the properties of the progress dialog
            self.dialog.create('Task Progress', f"Downloading playlist...")

            # Start the task in a separate thread or process
            # In this example, we execute the task in the main thread for simplicity

            try:           
                urllib.request.urlretrieve(Utils.get_playlist_url(), temp_file_path, reporthook = self.progress_callback)

                playlist_path = Utils.get_playlist_path()
                result = xbmcvfs.copy(temp_file_path, playlist_path)

                if not result:
                    LogManagement.error(f'Error copying playlist to {playlist_path}')    
            except:
                xbmcvfs.delete(temp_file_path)

            # Close the progress dialog
            self.dialog.close()

            LogManagement.info(f'Playlist downloaded to {Utils.get_playlist_path()}')
        else:
            xbmcvfs.copy(Utils.get_playlist_url(), Utils.get_playlist_path())

            LogManagement.info(f'Playlist copied to {Utils.get_playlist_path()}')

        LogManagement.info(f'Loaded playlist successfully.')

    def get_xmltv_file(self) -> str:
        LogManagement.info(f'Loading XmlTV from {Utils.get_xmltv_url()}.')

        LogManagement.info(f'XmlTV save path: {Utils.get_xmltv_path()}.')

        if xbmcvfs.exists(Utils.get_xmltv_path()):
            xbmcvfs.delete(Utils.get_xmltv_path())

        if Utils.get_xmltv_url().startswith('http') or Utils.get_xmltv_url().startswith('https'):
            if not xbmcvfs.exists(Utils.get_movie_output_path()):
                xbmcvfs.mkdirs(Utils.get_movie_output_path())

            self.dialog.create('Task Progress', f"Downloading XmlTV file...")

            try:           
                urllib.request.urlretrieve(Utils.get_xmltv_url(), Utils.get_xmltv_path(), reporthook = self.progress_callback)
                LogManagement.info(f'XmlTV file downloaded to {Utils.get_xmltv_path()}')                
            except Exception as e:
                LogManagement.error(f'Error downloading xml tv file: {e}')

            self.dialog.close()
        else:
            xbmcvfs.copy(Utils.get_xmltv_url(), Utils.get_xmltv_path())
            LogManagement.info(f'XmlTV file copied to {Utils.get_xmltv_path()}')

    def progress_callback(self, count, block_size, total_size):
        # Calculate the download percentage
        progress = count * block_size * 100 // total_size

        self.dialog.update(progress)

    def cleanup_filename(filename) -> str:
        pattern = r"[@$%&\\/:\*\?\"'<>\|~`#\^\+=\{\}\[\];!]"

        new_string = re.sub(pattern, "", filename)

        return(new_string)
    
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
