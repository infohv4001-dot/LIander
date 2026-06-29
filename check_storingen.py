import os
import requests
import json

WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')
API_URL = "https://services1.arcgis.com/v6W5HAVrpgSg3vts/ArcGIS/rest/services/IStoringen_Productie_V7/FeatureServer/0/query"
PARAMS = {
    "where": "STORING_GETROFFEN_POSTCODES LIKE '%4001%' OR STORING_GETROFFEN_POSTCODES LIKE '%4005%'",
    "outFields": "STORING_NUMMER,STORING_STATUS,STORING_GETROFFEN_POSTCODES",
    "f": "pjson"
}

def run():
    # 1. Haal de huidige data op
    try:
        response = requests.get(API_URL, params=PARAMS).json()
        huidige = {str(f['attributes']['STORING_NUMMER']): f['attributes']['STORING_STATUS'] for f in response.get('features', [])}
    except Exception as e:
        print(f"Fout bij API call: {e}")
        return

    # 2. Check of we een oude status hebben
    if not os.path.exists('status.json'):
        # Eerste run: alleen opslaan, niet melden
        with open('status.json', 'w') as f:
            json.dump(huidige, f)
        print("Initialisatie: status.json aangemaakt zonder meldingen.")
        
        # We moeten dit nog steeds committen, anders blijft hij elke 15 min opnieuw initialiseren
        push_to_git()
        return

    with open('status.json', 'r') as f:
        oude = json.load(f)

    # 3. Vergelijk en meld
    for id, status in huidige.items():
        if id not in oude:
            requests.post(WEBHOOK_URL, json={"content": f"⚠️ **Nieuwe storing ({id})!** Status: {status}"})
        elif status != oude[id]:
            requests.post(WEBHOOK_URL, json={"content": f"🔄 **Update storing ({id})!** Nieuwe status: {status}"})

    # 4. Opslaan als er echt iets veranderd is
    if huidige != oude:
        with open('status.json', 'w') as f:
            json.dump(huidige, f)
        push_to_git()

def push_to_git():
    os.system('git config --global user.name "bot"')
    os.system('git config --global user.email "bot@bot.com"')
    os.system('git add status.json')
    os.system('git commit -m "update status"')
    os.system('git push')

if __name__ == "__main__":
    run()
