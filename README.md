# DSBApi

> Eine API für die DSBMobile Vertretungsplan-Lösung, welche viele Schulen benutzen.

* Python 3
* Funktioniert Stand 07.11.2019 (Jetzt via Android-API (nach Problemen in 0.0.3), seit 2015 stable
* Aktuell in Version 0.0.10
* Aktuell nicht stable, das Encoding muss noch angepasst werden.
### Installation:
```pip3 install dsbapipy```

oder manuell vom Source Code.
### Datensatz:
> JSON Liste an Arrays. Ein Array sieht so aus:

| Key | Value | Notiz |
| --- | ---   | ---   |
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

### Implementierung:

```py
import dsbapi

dsbclient = dsbapi.DSBApi("username", "password")
entries = dsbclient.fetch_entries() # Rückgabe einer JSON Liste an Arrays
print(entries[0]["date"]) # Datum des ersten Eintrags
```
