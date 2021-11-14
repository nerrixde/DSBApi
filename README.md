
# DSBApi

> Eine API für die DSBMobile Vertretungsplan-Lösung, welche viele Schulen benutzen.

* Funktioniert Stand 10.11.21 (Jetzt via Android-API (nach Problemen in 0.0.3), seit 2015 stable
* Aktuell in Version 0.0.14
* Aktuell stable
* Units 2020 nicht vollständig unterstützt, PRs welcome, aber Kompatibilität berücksichtigen!

Bei Problemen und/oder Fragen, gerne ein "Issue" eröffnen. 

## Installation:

`pip install dsbapipy`
oder manuell:
`pip install git+https://github.com/nerrixDE/DSBApi.git#egg=dsbapipy`

## Datensatz:

> JSON Liste an Arrays. Ein Array sieht so aus:

| Key | Value | Notiz |
| --- | ---   | ---   |
| `type` | `Vertretung` | Art des Eintrags |
| `class` | `5D`  | Klasse |
| `lesson` | `12`  | Schulstunde |
| `room` | `R404`  | (Neuer) Raum |
| `new_subject` | `M-GK1`  | Neuer Kurs |
| `subject` | `IF-LK4`  | Ursprüngliches Fach / Kurs |
| `new_teacher` | `NEUM`  | Neuer Lehrer |
| `teacher` | `BIMM`  | Ursprünglicher Lehrer |
| `date` | `01.01.2019`  | Datum |
| `day` | `Montag`  | Wochentag |
| `updated` | `02.02.2019 12:13`  | Letztes Update |

## Hinweise zum Key "class"

Der key "class" wird speziell behandelt, indem der Inhalt der Schulklasse bei der Zeichenfolge "`, `" geteilt wird.
Diese Teilung wird verwendet um bei kombinierten Klasseneinträgen, die Daten für jede Klasse einzeln aufzusplitten.


## Implementierung:

### Beispiel 1

```py
import dsbapi

dsbclient = dsbapipy.DSBApi("benutzername", "passwort")
entries = dsbclient.fetch_entries()

for s in range(len(entries)):
  for i in range(len(entries[s])):
    print(entries[s][i]["date"])

```

### Beispiel 2: Anderes Tabellenformat
Schulen sind relativ frei in der Gestaltung Ihrer Datensätze. Daher kann der oben beschriebene Standard wiefolgt überschrieben werden:

```py
import dsbapi

ownFields = ['class','lesson','new_subject','room','subject','new_teacher','type','text']

dsbclient = dsbapipy.DSBApi("benutzername", "passwort", tablemapper=ownFields)
entries = dsbclient.fetch_entries()

for s in range(len(entries)):
  for i in range(len(entries[s])):
    print(entries[s][i]["date"])
```

### Beispiel 3: Nützliches Beispiel
Ein real-world Beispiel:

```py
import dsbapi as dsbapipy
import json
import datetime

days = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag", "Samstag","Sonntag"]
klasse = "10b
ownFields = ['class','lesson','new_subject','room','subject','new_teacher','type','text']
dsbclient = dsbapipy.DSBApi("benutzername", "passwort", tablemapper=ownFields)
entries  dsbclient.fetch_entries()
final = []

for s in range(len(entries)):
    for i in range(len(entries[s])):
        day = days[datetime.datetime.today().weekday() +1]
        if entries[s][i]["class"] == klasse:
            if entries[s][i]["day"] == day:
                lesson = entries[s][i]["lesson"]
                subject = entries[s][i]["new_subject"]
                teacher = entries[s][i]["room"]
                oldsubject = entries[s][i]["subject"]
                room = entries[s][i]["new_teacher"]
                vertreter = entries[s][i]["type"]
                text = entries[s][i]["text"]
                final.append({"lesson":lesson, "new_subject": subject, "room":room, "old_subject":oldsubject, "teacher":teacher, "type":vertreter, "text":text})

message = f"Am {day} gibt es {str(len(final))} Einträge. "
for s in final:
    message += f"In der {s['lesson']}. Stunde hast du {s['new_subject']} mit {s['teacher']} in {s['room']}. "
print(message)
                

```
