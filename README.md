# Geocathing

Een modern geocaching platform waar RFID tags worden gebruikt om caches te tracken en te loggen.

## Features

- RFID tag tracking systeem
- Interactieve wereldkaart met cache locaties
- Automatische locatie detectie via smartphone
- Logboek systeem voor cache vondsten
- Mogelijkheid om tags te verplaatsen naar nieuwe locaties

## Technische Stack

- Backend: Flask (Python)
- Frontend: HTML, CSS met variabelen, JavaScript
- Database: SQLite
- Kaart: Leaflet
- RFID: Web NFC API

## Setup

### Vereisten

- Python 3.8 of hoger
- Een moderne smartphone met NFC ondersteuning
- Een moderne webbrowser

### Installatie

1. Clone de repository
2. Maak een virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Op Windows: venv\Scripts\activate
   ```

3. Installeer dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start de development server:
   ```bash
   python app.py
   ```

## Project Structuur

```
geocathing/
├── static/           # CSS, JavaScript en andere statische bestanden
│   ├── css/         # Stylesheets
│   ├── js/          # JavaScript bestanden
│   └── img/         # Afbeeldingen
├── templates/       # HTML templates
├── app.py          # Flask applicatie
├── database.py     # Database configuratie
└── requirements.txt # Python dependencies
```

## Contributing

1. Fork de repository
2. Maak een nieuwe feature branch
3. Commit je changes
4. Push naar de branch
5. Maak een Pull Request

## License

MIT 