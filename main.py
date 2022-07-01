import os, requests, json
from urllib.request import urlopen
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError
from jsonpath_ng import parse
from halo import Halo
from PIL import Image, ImageFont, ImageDraw

spinner = Halo(text='Loading', spinner='dots', text_color='red')
spinner.start()

load_dotenv()

# Golbal Variables
# Get the API_KEY from https://developer.riotgames.com/ and Build your own .env file
# Regions: BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, TR1, RU
api_key = os.environ["API_KEY"]
watcher = LolWatcher(api_key)
region = 'EUW1' # Change it
name = 'redabel3' # Change it

def get_first_mastery(summoner_id):
    url = "https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summoner_id

    result = requests.get(url, headers={"X-Riot-Token": api_key})

    file_champs = urlopen('http://ddragon.leagueoflegends.com/cdn/12.12.1/data/en_US/champion.json')
    data_champs = json.loads(file_champs.read())['data']

    champ_id = int(result.json()[0]['championId'])
    
    all_ids = [match.value for match in parse('*.key').find(data_champs)]
    all_names = [match.value for match in parse('*.id').find(data_champs)]
    all_titles = [match.value for match in parse('*.title').find(data_champs)]

    for id, name, title in zip(all_ids, all_names, all_titles):
        if int(id) == champ_id:
            return name + " Main - " + title

def create_json_infos(summoner_id, ranked_stats, mastery):
    result_json = {}
    result_json["name"] = name
    result_json["summoner_id"] = summoner_id
    result_json["champ_mastery"] = mastery

    for obj in ranked_stats:
        if obj['queueType'] == 'RANKED_SOLO_5x5':
            result_json["rank"] = obj['tier'].title() + ' ' + obj['rank']
            result_json["wins"] = obj['wins']
            result_json["losses"] = obj['losses']
            result_json["winRate"] = (obj['wins'] * 100 // (obj['losses'] + obj['wins'])) 
    
    return result_json

def create_image(data, rank):
    img = Image.open('./Templates/Bg/'+rank+'BGR.png')

    I1 = ImageDraw.Draw(img)
    Bold_Font = ImageFont.truetype('./Templates/Montserrat/static/Montserrat-Bold.ttf', 96)
    ExtraL_Font = ImageFont.truetype('./Templates/Montserrat/static/Montserrat-ExtraLightItalic.ttf', 96)
    Bold4_Font = ImageFont.truetype('./Templates/Montserrat/static/Montserrat-Bold.ttf', 40)
    Regular4_Font = ImageFont.truetype('./Templates/Montserrat/static/Montserrat-Regular.ttf', 40)

    I1.text((47, 39), sum_info['name'] + ',\n' + sum_info['rank'], font=Bold_Font ,fill=(20, 20, 20))

    I1.text((47, 273), 'LOLStastyy', font=ExtraL_Font ,fill=(20, 20, 20))

    I1.text((47, 399), sum_info['champ_mastery'], font=Bold4_Font ,fill=(20, 20, 20))

    I1.text((47, 506), 'Win Rate', font=Regular4_Font ,fill=(20, 20, 20))
    I1.text((237, 506), str(sum_info['winRate']) + '%', font=Bold4_Font ,fill=(20, 20, 20))

    I1.text((47, 562), str(sum_info['wins']) + 'W', font=Bold4_Font ,fill=(78, 159, 13))
    I1.text((47, 615), str(sum_info['losses']) + 'L', font=Bold4_Font ,fill=(148, 25, 25))

    img.save("./LOLStatsyy.png")

    print("\nCheck the LOLStatsyy.png Image card")


try:
    player = watcher.summoner.by_name(region, name)
    ranked_stats = watcher.league.by_summoner(region, player['id'])

    summoner_id = ranked_stats[0]['summonerId']
    
    sum_info = create_json_infos(summoner_id, ranked_stats, get_first_mastery(summoner_id))
    
    if not (sum_info.get('rank') is None):
        with open('summoner_informations.json', 'r+') as f:
            data = json.load(f)
            for modif in data['modifications']:
                if modif['name'] == "Title":
                    modif['text'] = sum_info['name'] + ', ' + sum_info['rank']
                if modif['name'] == "MAIN":
                    modif['text'] = sum_info['champ_mastery']
                if modif['name'] == "Perc":
                    modif['text'] = str(sum_info['winRate']) + '%'
                if modif['name'] == "Losses":
                    modif['text'] = str(sum_info['losses']) + 'L'
                if modif['name'] == "Wins":
                    modif['text'] = str(sum_info['wins']) + 'W'
            f.seek(0)        
            json.dump(data, f, indent=4)
            f.truncate()
            print("\nCheck the summoner_informations File")

            create_image(sum_info, sum_info['rank'].split()[0])
    else:
        print("\nLOLStatsyy Only for Ranked Summoners")
    
except ApiError as err:
    if err.response.status_code == 429:
        spinner.text = 'We should retry in {} seconds.'.format(err.headers['Retry-After'])
    elif err.response.status_code == 404:
        spinner.text = 'Summoner with that ridiculous name not found.'
    else:
        raise

spinner.stop()