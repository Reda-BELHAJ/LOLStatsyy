# LOLStatsyy
 
LOLStatsyy is a card stat for league of legends built with Python and :
- riotwatcher
- jsonpath_ng
- halo
- pillow

```
halo==0.0.31
jsonpath_ng==1.5.3
Pillow==9.1.1
python-dotenv==0.20.0
requests==2.28.1
riotwatcher==3.2.3
```

And you can install the modules by:
```
pip install -r requirements.txt
```

Get the API_KEY from https://developer.riotgames.com/ and Build your own .env file
```
API_KEY=[API-KEY-HERE]
```
Change the region and the name in `main.py`
```
region = 'EUW1' # Change it
name = 'redabel3' # Change it
```