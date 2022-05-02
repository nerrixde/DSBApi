# -*- coding: utf-8 -*-
"""
DSBApi
An API for the DSBMobile substitution plan solution, which many schools use.
"""
__version_info__ = ('0', '0', '14')
__version__ = '.'.join(__version_info__)

import bs4
import json
import requests
import datetime
import gzip
import uuid
import base64

try:
    from PIL import Image
except:
    import Image
import pytesseract

class DSBApi:
    def __init__(self, username, password, tablemapper=['type','class','lesson','subject','room','new_subject','new_teacher','teacher']):
        """
        Class constructor for class DSBApi
        @param username: string, the username of the DSBMobile account
        @param password: string, the password of the DSBMobile account
        @param tablemapper: list, the field mapping of the DSBMobile tables (default: ['type','class','lesson','subject','room','new_subject','new_teacher','teacher'])
        @return: class
        @raise TypeError: If the attribute tablemapper is not of type list
        """
        self.DATA_URL = "https://app.dsbcontrol.de/JsonHandler.ashx/GetData"
        self.username = username
        self.password = password
        if not isinstance(tablemapper, list):
            raise TypeError('Attribute tablemapper is not of type list!')
        self.tablemapper = tablemapper
        
        # loop over tablemapper array and identify the keyword "class". The "class" will have a special operation in split up the datasets
        self.class_index = None
        i = 0
        while i < len(self.tablemapper):
            if self.tablemapper[i] == 'class':
                self.class_index = i
                break
            i += 1
       

    def fetch_entries(self, images=True):
        """
        Fetch all the DSBMobile entries
        @return: list, containing lists of DSBMobile entries from the tables or only the entries if just one table was received (default: empty list)
        @rais Exception: If the request to DSBMonile failed
        """
        # Iso format is for example 2019-10-29T19:20:31.875466
        current_time = datetime.datetime.now().isoformat()
        # Cut off last 3 digits and add 'Z' to get correct format
        current_time = current_time[:-3] + "Z"

        # Parameters required for the server to accept our data request
        params = {
            "UserId": self.username,
            "UserPw": self.password,
            "AppVersion": "2.5.9",
            "Language": "de",
            "OsVersion": "28 8.0",
            "AppId": str(uuid.uuid4()),
            "Device": "SM-G930F",
            "BundleId": "de.heinekingmedia.dsbmobile",
            "Date": current_time,
            "LastUpdate": current_time
        }
        # Convert params into the right format
        params_bytestring = json.dumps(params, separators=(',', ':')).encode("UTF-8")
        params_compressed = base64.b64encode(gzip.compress(params_bytestring)).decode("UTF-8")

        # Send the request
        json_data = {"req": {"Data": params_compressed, "DataType": 1}}
        timetable_data = requests.post(self.DATA_URL, json = json_data)

        # Decompress response
        data_compressed = json.loads(timetable_data.content)["d"]
        data = json.loads(gzip.decompress(base64.b64decode(data_compressed)))

        # validate response before proceed
        if data['Resultcode'] != 0:
            raise Exception(data['ResultStatusInfo'])
        
        # Find the timetable page, and extract the timetable URL from it
        final = []
        for page in data["ResultMenuItems"][0]["Childs"]:
                for child in page["Root"]["Childs"]:
                        if isinstance(child["Childs"], list):
                            for sub_child in child["Childs"]:
                                final.append(sub_child["Detail"])
                        else:
                            final.append(child["Childs"]["Detail"])
        if not final:
            raise Exception("Timetable data could not be found")
        output = []
        for entry in final:
            if entry.endswith(".htm") and not entry.endswith(".html") and not entry.endswith("news.htm"):
                output.append(self.fetch_timetable(entry))
            elif entry.endswith(".jpg") and images == True:
                output.append(self.fetch_img(entry))

        final = []
        for entry in output:
            if entry is not None:
                final.append(entry)

        output = final

        if len(output) == 1:
            return output[0]
        else:
            return output


    def fetch_img(self, imgurl):
        """
        Extract data from the image
        @param imgurl: string, the URL to the image
        @return: list, list of dicts
        @todo: Future use - implement OCR
        @raise Exception: If the function will be crawled, because the funbtion is not implemented yet
        """

        try:
            img = Image.open(io.BytesIO(requests.get(imgurl)))
        except:
            return  #haha this is quality coding surplus

        string = ""

        try:
            return  pytesseract.image_to_string(img)
        except TesseractError:
            raise Exception("You have to make the tesseract command accessible and work!")
            return None

    def fetch_timetable(self, timetableurl):
        """
        parse the timetableurl HTML page and return the parsed entries
        @param timetableurl: string, the URL to the timetable in HTML format
        @return: list, list of dicts
        """
        results = []
        sauce = requests.get(timetableurl).text
        soupi = bs4.BeautifulSoup(sauce, "html.parser")
        ind = -1
        for soup in soupi.find_all('table', {'class': 'mon_list'}):
            ind += 1
            updates = [o.p.findAll('span')[-1].next_sibling.split("Stand: ")[1] for o in soupi.findAll('table', {'class': 'mon_head'})][ind]
            titles = [o.text for o in soupi.findAll('div', {'class': 'mon_title'})][ind]
            date = titles.split(" ")[0]
            day = titles.split(" ")[1].split(", ")[0].replace(",", "")
            entries = soup.find_all("tr")
            entries.pop(0)
            for entry in entries:
                infos = entry.find_all("td")
                if len(infos) < 2:
                    continue
                
                # check if a "class" attribute is there, if yes, split the "class" value by "," to spread out the data rows for each school class
                if self.class_index != None:
                    class_array = infos[self.class_index].text.split(", ")
                else:
                    # define a dummy value if we don't have a class column (with keyword "class")
                    class_array = [ '---' ]
                for class_ in class_array:
                    new_entry = dict()
                    new_entry["date"] = date
                    new_entry["day"]  = day
                    new_entry["updated"] = updates
                    i = 0
                    while i < len(infos):
                        if i < len(self.tablemapper):
                            attribute = self.tablemapper[i]
                        else:
                            attribute = 'col' + str(i)
                        if attribute == 'class':
                            new_entry[attribute] = class_ if infos[i].text != "\xa0" else "---"
                        else:
                            new_entry[attribute] = infos[i].text if infos[i].text != "\xa0" else "---"
                        i += 1
                    results.append(new_entry)
        return results
