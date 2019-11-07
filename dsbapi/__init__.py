import bs4
import json
import requests
import datetime
import gzip
import uuid
import base64

class DSBApi:
    def __init__(self, username, password):
        self.DATA_URL = "https://app.dsbcontrol.de/JsonHandler.ashx/GetData"
        self.username = username
        self.password = password

    # Sends a data request to the server.
    # Returns the URL to the timetable HTML page
    def fetch_entries(self):
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
            "Device": "SM-G935F",
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
            elif entry.endswith(".jpg"):
                output.append(self.fetch_img(entry))
        if len(output) == 1:
            return output[0]
        else:
            return output
    def fetch_img(self, imgurl):
        return imgurl # TODO: Implement OCR
    def fetch_timetable(self, timetableurl):
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
                for class_ in infos[1].text.split(", "):
                    new_entry = {"type": infos[0].text if infos[0].text != "\xa0" else "---",
                        "class": class_ if infos[1].text != "\xa0" else "---",
                        "lesson": infos[2].text if infos[2].text != "\xa0" else "---",
                        "room": infos[4].text if infos[4].text != "\xa0" else "---",
                        "new_subject": infos[5].text if infos[5].text != "\xa0" else "---",
                        "subject": infos[3].text if infos[3].text != "\xa0" else "---",
                        "new_teacher": infos[6].text if infos[6].text != "\xa0" and infos[6].text != "+" else "---",
                        "teacher": infos[7].text if infos[7].text != "\xa0" and infos[7].text != "+" else "---",
                        "date": date,
                        "day": day,
                        "updated": updates}
                    results.append(new_entry)
        return results
