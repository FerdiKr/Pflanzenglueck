# Pflanzenglück

Ein einfaches Programm zur automatischen Bewässerung von Topfpflanzen oder ähnlichen Anwendungen mithilfe von online konfigurierbaren Bewässerungsregeln.

## Funktionen:

- Weboberfläche zur Konfiguration der Bewässerung
- Regel-Schema: Zu einer bestimmten Zeit und in einem bestimmten Intervall kann ein bestimmter Pin an einem Microcontroller für eine bestimmte Dauer an- oder ausgeschaltet werden
- Unterstützung mehrerer Benutzer
- Microcontroller-Programm für ESP32, das automatisch die Regeln online abfragt und entsprechend ausführt

## Kurzanleitung:

1. Installiere die erforderlichen Abhängigkeiten (requirements)
2. Füge einen Benutzer hinzu, indem du den Befehl `flask --app Pflanzenglueck adduser (username) (password)` ausführst
3. Hoste die Flask-App, z.B. mit Apache2
4. Melde dich an und lege Bewässerungsregeln fest
5. Konfiguriere die Datei `Pflanzenglueck_ESP.ino` (WiFi, Endpoint, API-Schlüssel - zu finden auf der Profilseite)
6. Flash die Datei `Pflanzenglueck_ESP.ino` auf einen entsprechenden Microcontroller (ESP32)
7. Verbinde Bewässerungsgeräte wie Magnetventile (ggf. über Relais oder Mosfets, falls eine höhere Spannung benötigt wird), die eine Wasserzufuhr aus einem höheren Reservoir öffnen oder schließen, oder Modellbau-Pumpen.

## FAQ:

**F: Warum ist das alles so überkompliziert aufgebaut, siehe WebComponents, optionale Azure-Integration und Localization-System?**  
A: Diese Systeme wurden für andere, komplexere Anwendungen entwickelt und hier einfach aus Gewohnheit weiterverwendet.

**F: Warum sieht der Code-Stil teilweise so unterschiedlich aus?**  
A: Geschrieben mit freundlicher Unterstützung von ChatGPT ^^
