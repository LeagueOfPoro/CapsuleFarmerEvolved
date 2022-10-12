import cloudscraper
import asyncio
from pprint import pprint
from bs4 import BeautifulSoup
import yaml

class SessionManager:
    def __init__(self):
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=True)

    def login(self, username, password):
        # Get necessary cookies from the main page
        res = self.client.get("https://login.leagueoflegends.com/?redirect_uri=https://lolesports.com/&lang=en")
        
        # Submit credentials
        data = {"type":"auth", "username":username, "password":password, "remember": True, "language":"en_US"}
        res = self.client.put("https://auth.riotgames.com/api/v1/authorization", json=data)
        resJson = res.json()
        if resJson.get("type", "") and resJson["response"].get("parameters", "") and resJson["response"]["parameters"].get("uri", ""):
            # Finish OAuth2 login
            res = self.client.get(resJson["response"]["parameters"]["uri"])
            
            # Login to lolesports.com, riotgames.com, and playvalorant.com
            token, state = self.__getLoginTokens(res.text)
            if token and state:
                data = {"token": token, "state": state}
                self.client.post("https://login.riotgames.com/sso/login", data=data)
                self.client.post("https://login.lolesports.com/sso/login", data=data)
                self.client.post("https://login.playvalorant.com/sso/login", data=data)
                
                res = self.client.post("https://login.leagueoflegends.com/sso/callback", data=data)

                # Get access token for the first time
                
                headers= {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com", "x-api-key":"0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
                res = self.client.get("https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)

                headers= {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com"}
                res = self.client.get("https://account.rewards.lolesports.com/v1/session/token", headers=headers) # Why is it returning 400???
            
        # pprint(self.client.cookies.get_dict())
    
    def __getLoginTokens(self, form):
        page = BeautifulSoup(form)
        if tokenInput := page.find("input", {"name" : "token"}):
            token = tokenInput.get("value", "")
        if tokenInput := page.find("input", {"name" : "state"}):
            state = tokenInput.get("value", "")                
        return token, state


sm = SessionManager()

with open("config.yaml", "r",  encoding='utf-8') as f:
    config = yaml.safe_load(f)
    sm.login(config["username"], config["password"])