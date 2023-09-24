import re
from resources.lib.GroupManagement import Groups

class ExtM3UEntry:
    extinf = None
    url = None
    id = None
    name = None
    title = None
    subfolder =  None
    filename =  None
    logo =er =  None
    include = None    
    group_title = None
    type = None

    num_other_skipped = None
    num_movies_skipped = None
    num_series_skipped = None

    # @property
    # def name(self):
    #     self.name = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', self.name)
    #     return self.name

    # @name.setter
    # def name(self, value):
    #     # You can add validation or custom logic for setting tvg_name
    #     tvgname = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', tvgname)
    #     self.name = value    

    def __init__(self, extinf=None, extinf_url=None):
        self.extinf = extinf  # EXTINF extinf_line
        self.url = extinf_url

        self.parse_extinf(extinf)
        self.set_include(extinf)

        if '[Series]' in extinf or 'Series:' in extinf:
            self.type = 'Series'
        elif '[VOD]' in extinf or 'VOD:' in extinf or '(VOD)' in extinf:
            self.type = 'Movies'
        else:
            self.type = 'Other'


    def parse_extinf(self, extinf):
        if extinf:
            # Split the EXTINF extinf_line to extract properties
            parts = extinf.split(' ')
            for part in parts:
                if part.startswith('tvg-id='):
                    self.id = part.split('tvg-id=')[1].strip('"')
                elif part.startswith('tvg-name='):
                    self.name = part.split('tvg-name=')[1].strip('"')
                elif part.startswith('tvg-logo='):
                    self.logo = part.split('tvg-logo=')[1].strip('"')
                elif part.startswith('group-title='):
                    self.group_title = part.split('group-title=')[1].strip('"')

            # Remove unsafe file and folder characters from title
            #self.filename = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', self.name)
            if self.type == 'Series':
                self.title = self.get_series_title_from_tvgname(self.name)
                self.subfolder = self.get_series_subfolder_from_tvgname(self.name)
                self.filename = self.get_series_filename_from_tvgname(self.name)
            elif self.type == 'Movies':
                self.title = self.get_movie_title_from_tvgname(self.name)
                self.subfolder = self.get_movie_filename_from_tvgname(self.name)                
                self.filename = self.get_movie_filename_from_tvgname(self.name)
            else:
                self.num_other_skipped += 1

    def __str__(self):
        return f"#EXTINF:-1 tvg-id=\"{self.id}\" tvg-name=\"{self.name}\" tvg-logo=\"{self.logo}\" group-title=\"{self.group_title}\",{self.extinf}\n{self.extinf_url}"

    def set_include(self, extinf_line):
        tvgIdMatch = re.search('tvg-id=""', extinf_line)

        self.include = False        

        if not tvgIdMatch:
            return

        if self.group_title is None:
            return

        # Check if group should be included
        if not Groups.check_group_inclusion(self.group_title):
            return

        self.include = True
        return


    # This is a movie [PRE] [2022] ->
    # This is a movie
    def get_movie_title_from_tvgname(self, tvgname):
        pattern = r"\s*\[[^\]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    # This is a movie [PRE] [2022] ->
    # This is a movie [2022]
    def get_movie_filename_from_tvgname(self, tvgname):
        pattern = r"\[(?!\d{4}\])[^]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    # This is a series - S01 This is a series - S01E01
    # This is a series -
    def get_series_title_from_tvgname(self, tvgname):
        pattern = r'^(.*?) S\d+'
        match = re.search(pattern, tvgname)

        if match:
            title = match[1]
        else:
            return('')
        
        return(title)

    # This is a series - S01 This is a series - S01E01
    # This is a series - S01
    def get_series_subfolder_from_tvgname(self, tvgname):
        pattern = r'^(.*?)\bS\d{1,2}'
        match = re.match(pattern, tvgname)

        if match:
            subfolder = match[0]
        else:
            return('')
        
        return(subfolder)

    # This is a series - S01 This is a series - S01E01
    #                        This is a series - S01E01
    def get_series_filename_from_tvgname(self, tvgname):
        pattern = r'^.*S\d{2}\s+(.*)$'
        match = re.search(pattern, tvgname)

        if match:
            filename = match[1]
        else:
            return('')
        
        return(filename)

class ExtM3UEntry:
    extinf = None
    url = None
    id = None
    name = None
    title = None
    subfolder =  None
    filename =  None
    logo =er =  None
    include = None    
    group_title = None
    type = None

    num_other_skipped = None
    num_movies_skipped = None
    num_series_skipped = None

    # @property
    # def name(self):
    #     self.name = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', self.name)
    #     return self.name

    # @name.setter
    # def name(self, value):
    #     # You can add validation or custom logic for setting tvg_name
    #     tvgname = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', tvgname)
    #     self.name = value    

    def __init__(self, extinf=None, extinf_url=None):
        self.extinf = extinf  # EXTINF extinf_line
        self.url = extinf_url

        self.parse_extinf(extinf)
        self.set_include(extinf)

        if '[Series]' in extinf or 'Series:' in extinf:
            self.type = 'Series'
        elif '[VOD]' in extinf or 'VOD:' in extinf or '(VOD)' in extinf:
            self.type = 'Movies'
        else:
            self.type = 'Other'


    def parse_extinf(self, extinf):
        if extinf:
            # Split the EXTINF extinf_line to extract properties
            parts = extinf.split(' ')
            for part in parts:
                if part.startswith('tvg-id='):
                    self.id = part.split('tvg-id=')[1].strip('"')
                elif part.startswith('tvg-name='):
                    self.name = part.split('tvg-name=')[1].strip('"')
                elif part.startswith('tvg-logo='):
                    self.logo = part.split('tvg-logo=')[1].strip('"')
                elif part.startswith('group-title='):
                    self.group_title = part.split('group-title=')[1].strip('"')

            # Remove unsafe file and folder characters from title
            #self.filename = re.sub(r'[<>:"/\\|?*\x00-\x1f.]', '', self.name)
            if self.type == 'Series':
                self.title = self.get_series_title_from_tvgname(self.name)
                self.subfolder = self.get_series_subfolder_from_tvgname(self.name)
                self.filename = self.get_series_filename_from_tvgname(self.name)
            elif self.type == 'Movies':
                self.title = self.get_movie_title_from_tvgname(self.name)
                self.subfolder = self.get_movie_filename_from_tvgname(self.name)                
                self.filename = self.get_movie_filename_from_tvgname(self.name)
            else:
                self.num_other_skipped += 1

    def __str__(self):
        return f"#EXTINF:-1 tvg-id=\"{self.id}\" tvg-name=\"{self.name}\" tvg-logo=\"{self.logo}\" group-title=\"{self.group_title}\",{self.extinf}\n{self.extinf_url}"

    def set_include(self, extinf_line):
        tvgIdMatch = re.search('tvg-id=""', extinf_line)

        self.include = False        

        if not tvgIdMatch:
            return

        if self.group_title is None:
            return

        # Check if group should be included
        if not Groups.check_group_inclusion(self.group_title):
            return

        self.include = True
        return


    # This is a movie [PRE] [2022] ->
    # This is a movie
    def get_movie_title_from_tvgname(self, tvgname):
        pattern = r"\s*\[[^\]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    # This is a movie [PRE] [2022] ->
    # This is a movie [2022]
    def get_movie_filename_from_tvgname(self, tvgname):
        pattern = r"\[(?!\d{4}\])[^]]*\]"
        match = re.sub(pattern, "", tvgname)

        return(match)

    # This is a series - S01 This is a series - S01E01
    # This is a series -
    def get_series_title_from_tvgname(self, tvgname):
        pattern = r'^(.*?) S\d+'
        match = re.search(pattern, tvgname)

        if match:
            title = match[1]
        else:
            return('')
        
        return(title)

    # This is a series - S01 This is a series - S01E01
    # This is a series - S01
    def get_series_subfolder_from_tvgname(self, tvgname):
        pattern = r'^(.*?)\bS\d{1,2}'
        match = re.match(pattern, tvgname)

        if match:
            subfolder = match[0]
        else:
            return('')
        
        return(subfolder)

    # This is a series - S01 This is a series - S01E01
    #                        This is a series - S01E01
    def get_series_filename_from_tvgname(self, tvgname):
        pattern = r'^.*S\d{2}\s+(.*)$'
        match = re.search(pattern, tvgname)

        if match:
            filename = match[1]
        else:
            return('')
        
        return(filename)

