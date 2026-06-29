import os
import requests
import json
import subprocess

WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

API_URL = "https://services1.arcgis.com/v6W5HAVrpgSg3vts/ArcGIS/rest/services/IStoringen_Productie_V7/FeatureServer/0/query"

PARAMS = {
    "where": "STORING_GETROFFEN_POSTCODES LIKE '%4001%' OR STORING_GETROFFEN_POSTCODES LIKE '%4005%' OR STORING_GETROFFEN_POSTCODES LIKE '%6612%'",
    "outFields": "STORING_NUMMER,STORING_STATUS,STORING_GETROFFEN_POSTCODES",
    "f": "pjson"
}


def run():
    print("Script gestart")

    # 1. API call
    try:
        r = requests.get(API_URL, params=PARAMS, timeout=20)
        r.raise_for_status()
        data = r.json()

        huidige = {
            str(f['attributes']['STORING_NUMMER']):
            f['attributes']['STORING_STATUS']
            for f in data.get('features', [])
        }

    except Exception as e:
        print(f"Fout bij API call: {e}")
        return

    # 2. eerste run
    if not os.path.exists('status.json'):
        with open('status.json', 'w') as f:
            json.dump(huidige, f)

        print("Initialisatie status.json")

        push_to_git()
        return

    with open('status.json', 'r') as f:
        oude = json.load(f)

    changed = False

    # 3. vergelijken + discord
    for id, status in huidige.items():
        if id not in oude:
            send_discord(f"⚠️ Nieuwe storing ({id})! Status: {status}")
            changed = True

        elif status != oude[id]:
            send_discord(f"🔄 Update storing ({id})! Nieuwe status: {status}")
            changed = True

    # 4. opslaan alleen bij wijziging
    if huidige != oude:
        with open('status.json', 'w') as f:
            json.dump(huidige, f)

        push_to_git()
    else:
        print("Geen wijzigingen")


def send_discord(message):
    if not WEBHOOK_URL:
        print("Geen webhook ingesteld")
        return

    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Discord fout: {e}")


def push_to_git():
    print("Git commit start")

    subprocess.run(["git", "config", "--global", "user.name", "bot"])
    subprocess.run(["git", "config", "--global", "user.email", "bot@bot.com"])

    subprocess.run(["git", "add", "status.json"])

    result = subprocess.run(
        ["git", "commit", "-m", "update status"],
        capture_output=True,
        text=True
    )

    if "nothing to commit" in result.stdout.lower():
        print("Geen commit nodig")
        return

    subprocess.run(["git", "push"], check=True)
    print("Push voltooid")


if __name__ == "__main__":
    run()
