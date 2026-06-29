import os
import requests

# Instellingen
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')
API_URL = "https://services1.arcgis.com/v6W5HAVrpgSg3vts/ArcGIS/rest/services/IStoringen_Productie_V7/FeatureServer/0/query"
PARAMS = {
    "where": "postcode IN ('4001', '4005')",
    "outFields": "postcode,omschrijving",
    "f": "pjson"
}

# --- TEST MODUS ---
# Zet TEST_MODE op True om een testbericht te sturen
TEST_MODE = False 
# ------------------

def check_storingen():
    if TEST_MODE:
        features = [{'attributes': {'postcode': 'TEST', 'omschrijving': 'Dit is een testbericht om de verbinding te controleren.'}}]
    else:
        try:
            response = requests.get(API_URL, params=PARAMS)
            response.raise_for_status()
            features = response.json().get('features', [])
        except Exception as e:
            print(f"Fout bij het ophalen van data: {e}")
            return

    if features:
        for f in features:
            attr = f['attributes']
            msg = f"⚠️ **Storing in postcode {attr['postcode']}!**\nOmschrijving: {attr['omschrijving']}"
            requests.post(WEBHOOK_URL, json={"content": msg})
    else:
        print("Geen storingen gevonden.")

if __name__ == "__main__":
    check_storingen()
