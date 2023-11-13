import requests
import json
import os
import time
from datetime import date

#print('getting credits footer')
#CREDITS_FOOTER = requests.get('https://raw.githubusercontent.com/RagingEnby/SkypixelRepo/main/credit_footer.txt').text
CREDITS_FOOTER = 'Made by @ragingenby'
#print('got credits footer!\n\n')
CREDITS_IMAGE = 'https://github.com/RagingEnby/SkypixelRepo/blob/main/pfp.png?raw=true'

API_URL = "https://api.antisniper.net/v2/resources/ranks?rank={}&key={}"
SCAN_RANKS = ["gm", "admin", "youtube"]
ANTISNIPER_API_KEY = 'dddaff83-4b8a-4e0b-931b-51915afc5556'
BOT_NAME = "Skypixel"
BOT_AVATAR = "https://github.com/RagingEnby/SkypixelRepo/blob/main/skypixel.png?raw=true"
RANKS_DIR = "ranks/"
RANKS_HISTORY_DIR = "ranks/history/"
CSV_DIR = "ranks/spreadsheets/"
FIRST_EVER_RUN = False

def fetch_rank_data(scan_rank):
  url = API_URL.format(scan_rank, ANTISNIPER_API_KEY)
  response = requests.get(url)
  if response.status_code == 200:
    return response.json()["data"]
  else:
    return load_rank_data(scan_rank)
  
def save_rank_data(scan_rank, data):
    with open(f"{RANKS_DIR}/{scan_rank}.json", "w") as file:
      json.dump(data, file, indent=2)
      file.close()

def load_rank_data(scan_rank):
    file_path = os.path.join(f"{RANKS_DIR}/{scan_rank}.json")
    try:
        with open(file_path, "r") as file:
            return json.load(file)
            file.close()
    except Exception as e:
        print(f'Error while loading {scan_rank}: {e}')
        rank_data = fetch_rank_data(scan_rank)
        with open(file_path, 'w') as file:
            json.dump(rank_data, file, indent=2)
        return rank_data

def compare_rank_data(scan_rank, new_data, old_data):
    new_players = {player["uuid"]: player["ign"] for player in new_data}
    old_players = {player["uuid"]: player["ign"] for player in old_data}
    rank_change = False
    for uuid, ign in old_players.items():
        if uuid not in new_players:
            rank_change = True
            print(f"{ign} has lost [{scan_rank.upper()}] rank")
            DO_UPDATE_WEBHOOK(ign, scan_rank, "removed", ign)
        elif new_players[uuid] != ign:
          print('new_players[uuid] != ign')
          print(f'{new_players[uuid]} != {ign}')
          mojang_response = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
          mojang_response_ign = mojang_response['name']
          if mojang_response_ign == new_players[uuid]:
            rank_change = True
            print(f"[{scan_rank.upper()}] {ign} has changed their username to {scan_rank} {new_players[uuid]}")
            DO_UPDATE_WEBHOOK(new_players[uuid], scan_rank, "changed", ign)
          else:
            print('mojang_response_ign != new_players[uuid]')
            print(f'{mojang_response_ign} != {new_players[uuid]}')

    for uuid, ign in new_players.items():
        if uuid not in old_players:
          rank_change = True
          print(f"{ign} now has [{scan_rank.upper()}] rank")            
          DO_UPDATE_WEBHOOK(ign, scan_rank, "added", ign)
    if rank_change:
      with open(f'{CSV_DIR}/{scan_rank}.csv', 'a') as file:
        file.write(f'{date.today().strftime("%m/%d/%y")},{len(new_players)}\n')
      with open(f'{RANKS_HISTORY_DIR}/{scan_rank}/{round(time.time())}.json', 'w') as file:
        json.dump(new_data, file, indent=2)


# IGN, admin/gm/youtube, added/removed/changed, OLD_IGN
def DO_UPDATE_WEBHOOK(player, rank, status, OLD_IGN):
  if rank == "admin": 
    WEBHOOK = "https://discord.com/api/webhooks/1121130635021529260/UoZ0FFH7zEFLoMtDgDp0u0LkrbUMFpVnq1_9PdNhJYGwaR8DKY-PkyZt19Xz19fCcrev"
    embed_color = 16733525
    RANK_EMOJIS = "<:admin1:1121151231805628416><:admin2:1121151232761929728><:admin3:1121151234536120461><:admin4:1121151235702145066>"
    
  elif rank == "gm": 
    WEBHOOK = "https://discord.com/api/webhooks/1121130945106415686/INnaKEfTB6Nyt11Bv7uzjo-P2A2w7YFxk9KiMptVvEFisGEHQOLZfwhQSfLVsVefTX7z"
    embed_color = 43520
    RANK_EMOJIS = "<:gm1:1121151257403478221><:gm2:1121151259831980062> "

  elif rank == "youtube": 
    WEBHOOK = "https://discord.com/api/webhooks/1121131007496691752/7jysfKFusB8xqEYK3wCtP4lIHO1HCXE6-5LYJ_0kdx5nI0BaYjUJE8vg4h-jKPJ7CIQC"
    embed_color = 16733525
    RANK_EMOJIS = "<:yt1:1121150697266761778><:yt2:1121150699447799848><:yt3:1121150700643160174><:yt4:1121150701653983234><:yt5:1121150703059091577> "
    
  rank_upper = rank.upper()
  if status == "removed":
    title = f"{player} no longer has [{rank_upper}] rank!"
  elif status == "added":
    title = f"{player} now has [{rank_upper}] rank!"
  elif status == "changed":
    title = f"{OLD_IGN} has changed their IGN to {player}"

  SEND_UPDATE_WEBHOOK(title, embed_color, player, WEBHOOK)
    

def SEND_UPDATE_WEBHOOK(title, embed_color, player, WEBHOOK):
  print('sending webhook...')
  embed = {
  "content": "<@&1122272183733977249>",
  "embeds": [
    {
      "title": f"{title}",
      "color": f"{embed_color}",
      "author": {
        "name": f"{player}",
        "url": f"https://plancke.io/hypixel/player/stats/{player}",
        "icon_url": f"https://mc-heads.net/avatar/{player}.png"
      },
      "footer": {
        "text": CREDITS_FOOTER,
        "icon_url": CREDITS_IMAGE
      }
    }
  ],
  "username": BOT_NAME,
  "avatar_url": BOT_AVATAR
  }
  try:
    response = requests.post(WEBHOOK, data=json.dumps(embed), headers={"Content-Type": "application/json"})
    print(response)
  except Exception as e:
    print(e)
    time.sleep(10)
    SEND_UPDATE_WEBHOOK(title, embed_color, player, WEBHOOK)

  print('sent webhook!')

while True:
  print('Starting scan...')
  if not FIRST_EVER_RUN:
    for scan_rank in SCAN_RANKS:
      print(f'Scanning [{scan_rank.upper()}] rank')
      old_data = load_rank_data(scan_rank)
      if old_data is not None:
        new_data = fetch_rank_data(scan_rank)
        save_rank_data(scan_rank, new_data)
        if new_data is not None:
          compare_rank_data(scan_rank, new_data, old_data)
  else:
    print('First run detected!')
    for scan_rank in SCAN_RANKS:
      save_rank_data(scan_rank, fetch_rank_data(scan_rank))
  print('Finished scan!\n')
  time.sleep(240)