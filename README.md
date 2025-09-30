# Pokémon Team Editor

Ein Desktop-Tool zum Erstellen, Bearbeiten und Analysieren von Pokémon-Teams. Bietet Teamverwaltung, Anzeige von Pokémon-Daten und KI-gestützte Tipps vom "Prof. Eich"-Advisor.

## Funktionen

- **Teamverwaltung**
  - Bis zu 6 Pokémon pro Team.
  - Speichern und Laden von Teams als JSON-Dateien.
  - Eingabe von Name, Level, Typen, Moves, Stärken und Schwächen.

- **Pokémon-Daten**
  - Anzeige von Bildern, Typen, Moves und Basisinfos.
  - Unterstützung für verschiedene Spielversionen.
  - Dynamische Anpassung der Anzeigegröße und Schriftgrößen.

- **AI-Advisor**
  - Stelle Fragen an einen KI-basierten Pokémon-Advisor im Stil von Professor Eich.
  - Antworten werden im UI angezeigt.
  - Scrollbares Antwortfeld mit fester Höhe.

- **Benutzerfreundlichkeit**
  - Responsive UI mit Grid-Layout.
  - Eingabeprüfungen und Fehlermeldungen.
  - Schnelle Ladezeiten durch Threading.

## Installation

1. Repository klonen:
```bash
git clone https://github.com/RoccoDr02/PokeHelper.git
cd PokeHelper
```

2. Virtuelle Umgebung erstellen (optional):
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Abhängigkeiten installieren:
```
pip install -r requirements.txt
```
4. OpenAI API Key in .env Datei eintragen:
```
OPENAI_KEY=dein_api_key
```
5. Nutzung
```
python main.py
```
## Hinweis

Dies ist **nicht die finale Version** des Pokémon Team Editors.  
Das Projekt wird weiterhin aktiv entwickelt und erhält in Zukunft Updates, neue Funktionen und Verbesserungen.
