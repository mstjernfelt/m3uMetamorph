import xml.etree.ElementTree as ET

class EpgParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.programs = []

    def parse(self):
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            for program in root.findall('.//program'):
                title = program.find('title').text
                start_time = program.find('start_time').text
                end_time = program.find('end_time').text
                description = program.find('description').text

                self.programs.append({
                    'title': title,
                    'start_time': start_time,
                    'end_time': end_time,
                    'description': description
                })
        except ET.ParseError:
            print(f"Error parsing {self.xml_file}")

    def get_programs(self):
        return self.programs

# Example usage:
if __name__ == "__main__":
    epg_parser = EpgParser('your_epg_file.xml')
    epg_parser.parse()
    
    programs = epg_parser.get_programs()

    for program in programs:
        print("Title:", program['title'])
        print("Start Time:", program['start_time'])
        print("End Time:", program['end_time'])
        print("Description:", program['description'])
        print()
