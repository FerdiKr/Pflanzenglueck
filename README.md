Ein einfaches Programm zur automatischen Bewässerung von Topfpflanzen o.ä. mittels online konfigurierbarer Bewässerungsregeln.
Features:
- Weboberfläche zum Konfigurieren der Bewässerung
- Schema der Regeln: Zu einer bestimmten Zeit und in einem bestimmten Intervall kann ein bestimmter Pin an einem Microcontroller für eine bestimmte Dauer an- oder ausgeschaltet werden
- Unterstützt mehrere Benutzer
- Microcontroller-Programm für ESP32, das automatisch die Regeln online abfragt und entsprechend ausführt

Kurzanleitung:
- requirements installieren
- mittels flask --app Pflanzenglueck adduser (username) (password) Nutzer hinzufügen
- Flask-app hosten, z.B. mit apache2
- Einloggen, Regeln anlegen
- Pflanzenglueck_ESP.ino konfigurieren (Wifi, endpoint, api_key (zu finden auf der Seite unter Profil))
- Pflanzenglueck_ESP.ino auf einen entsprechenden Microcontroller (ESP32) flashen
- Bewässerungsgeräte anschließen: z.B. Magnetventile (ggf. über Relais oder Mosfets falls höhere Spannung benötigt), die eine Wasserzufuhr aus einem höheren Reservoir öffnen oder schließen, oder Modellbau-Pumpen

FAQ:
 F: Warum ist das alles so überkompliziert aufgebaut, siehe WebComponents und localization-System?
 A: Diese Systeme wurden für andere, komplexere Anwendungen entwickelt und hier einfach aus Gewohnheit weiterverwendet

 F: Warum sieht der Code-Stil teilweise so unterschiedlich aus?
 A: Geschrieben mit freundlicher Unterstützung von ChatGPT ^^