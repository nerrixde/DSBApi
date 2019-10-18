import bs4
import json
import requests
import datetime
import io
import gzip
import base64

class DSBApi:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0"

    def fetch_api(self):
        s = requests.Session()
        form_token_getter = s.request("GET", "https://www.dsbmobile.de/Login.aspx?ReturnUrl=/")
        form_token_soup = bs4.BeautifulSoup(form_token_getter.text, "html.parser")
        viewstate = form_token_soup.find("input", {"name":"__VIEWSTATE"})["value"]
        viewstategenerator = form_token_soup.find("input", {"name":"__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = form_token_soup.find("input", {"name":"__EVENTVALIDATION"})["value"]
        form_login_data = {"__LASTFOCUS":(None,""),"__VIEWSTATE":(None,viewstate),"__VIEWSTATEGENERATOR":(None,viewstategenerator),"__EVENTTARGET":(None,""),"__EVENTARGUMENT":(None,""),"__EVENTVALIDATION":(None,eventvalidation),"txtUser":(None,self.username),"txtPass":(None,self.password),"ctl03":(None,"Anmelden")}
        s.request("POST", "https://www.dsbmobile.de/Login.aspx?ReturnUrl=/", files=form_login_data, headers = {'User-Agent': self.user_agent})
        current_time = datetime.datetime.now().isoformat()
        current_time = current_time.split(".")[0] + "." + current_time.split(".")[1][:3] + "Z"
        innerDATA = {"UserId":"","UserPw":"","Abos":[],"AppVersion":"2.3","Language":"de","OsVersion":self.user_agent,"AppId":"","Device":"WebApp","PushId":"","BundleId":"de.heinekingmedia.inhouse.dsbmobile.web","Date":current_time,"LastUpdate":current_time}
        jsonStream = io.BytesIO()
        with gzip.open(filename=jsonStream, mode='wt') as streamReader:
            streamReader.write(json.dumps(innerDATA, separators=(',', ':')))
        timetable_data = s.request("POST", "https://www.dsbmobile.de/JsonHandlerWeb.ashx/GetData", headers = {'User-Agent': self.user_agent, "Content-Type": "application/json;charset=utf-8", "Referer": "https://www.dsbmobile.de/default.aspx"}, json = {"req": {"Data": base64.encodebytes(jsonStream.getvalue()).decode("utf-8"), "DataType": 1}})
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
