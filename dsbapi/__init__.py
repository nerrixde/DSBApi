import bs4
import json
import requests
import datetime
import io
import gzip
import uuid
import base64

class DSBApi:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def fetch_api(self):
        current_time = datetime.datetime.now().isoformat()
        current_time = current_time.split(".")[0] + "." + current_time.split(".")[1][:3] + "Z"
        innerDATA = {"UserId":self.username,"UserPw":self.password,"AppVersion":"2.5.9","Language":"de","OsVersion":"28 9.0","AppId":str(uuid.uuid4()),"Device":"SM-G935F","PushId":"","BundleId":"de.heinekingmedia.dsbmobile","Date":current_time,"LastUpdate":current_time}
        jsonStream = io.BytesIO()
        with gzip.open(filename=jsonStream, mode='wt') as streamReader:
            streamReader.write(json.dumps(innerDATA, separators=(',', ':')))
        timetable_data = requests.request("POST", "https://app.dsbcontrol.de/JsonHandler.ashx/GetData", json = {"req": {"Data": base64.encodebytes(jsonStream.getvalue()).decode("utf-8"), "DataType": 1}})
        return json.loads(gzip.decompress(base64.b64decode(json.loads(timetable_data.text)["d"])))["ResultMenuItems"][0]["Childs"][0]["Root"]["Childs"][0]["Childs"][0]["Detail"]

    def fetch_entries(self):
        timetable = self.fetch_api()
        results = []
        sauce = requests.get(timetable).text
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
