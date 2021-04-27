# DSBApi

> Eine API für die DSBMobile Vertretungsplan-Lösung, welche viele Schulen benutzen.

* Python 3
* Funktioniert Stand 02.10.2020 (Jetzt via Android-API (nach Problemen in 0.0.3), seit 2015 stable
* Aktuell in Version 0.0.14
* Aktuell stable
* Units 2020 nicht vollständig unterstützt, PRs welcome, aber Kompatibilität berücksichtigen!

## Installation:

`pip3 install dsbapipy`

oder manuell vom Source Code.

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

dsbclient = dsbapi.DSBApi("username", "password")
entries = dsbclient.fetch_entries() # Rückgabe einer JSON Liste an Arrays
print(entries[0]["date"]) # Datum des ersten Eintrags
```

### Beispiel 2: Anderes Tabellenformat
Schulen sind relativ frei in der Gestaltung Ihrer Datensätze. Daher kann der oben beschriebene Standard wiefolgt überschrieben werden:

```py
import dsbapi

ownFields = ['class','lesson','new_subject','room','subject','new_teacher','type','text']

dsbclient = dsbapi.DSBApi("username", "password", tablemapper=ownFields)
entries = dsbclient.fetch_entries() # Rückgabe einer JSON Liste an Arrays
print(entries[0]["date"]) # Datum des ersten Eintrags
```