from Logger.Logger import Logger
import cloudscraper
import asyncio
from pprint import pprint
from bs4 import BeautifulSoup
import yaml
import logging
from datetime import timedelta
import time
import threading

class Browser:
    SESSION_REFRESH_INTERVAL = 1800.0

    def __init__(self, log):
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=True)
        self.log = log

    # Initial login
    def login(self, username, password):
        # Get necessary cookies from the main page
        self.client.get("https://login.leagueoflegends.com/?redirect_uri=https://lolesports.com/&lang=en")
        
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

                # Get access and entitlement tokens for the first time
                headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com"}
                resAccessToken = self.client.get("https://account.rewards.lolesports.com/v1/session/token", headers=headers)
                resEntitlementToken = self.client.get("https://entitlements.rewards.lolesports.com/v1/entitlements/?token=true", headers=headers)
                if resAccessToken.status_code == 200 and resEntitlementToken.status_code == 200:
                    self.maintainSession()
                    return True
        return False
    
    # Refresh access and entitlement tokens
    def refreshTokens(self):
        headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com"}
        resAccessToken = self.client.get("https://account.rewards.lolesports.com/v1/session/refresh", headers=headers)
        resEntitlementToken = self.client.get("https://entitlements.rewards.lolesports.com/v1/entitlements/?token=true", headers=headers)
        if resAccessToken.status_code == 200 and resEntitlementToken.status_code == 200:
            self.maintainSession()
        else:
            self.log.error("Failed to refresh session")

    def maintainSession(self):
        self.refreshTimer = threading.Timer(Browser.SESSION_REFRESH_INTERVAL, self.refreshTokens)
        self.refreshTimer.start()
    
    def stopMaintaininingSession(self):
        self.refreshTimer.cancel()

    def getLiveMatches(self):
        headers= {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com", "x-api-key":"0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = self.client.get("https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)

    def __getLoginTokens(self, form):
        page = BeautifulSoup(form, features="html.parser")
        token = None
        state = None
        if tokenInput := page.find("input", {"name" : "token"}):
            token = tokenInput.get("value", "")
        if tokenInput := page.find("input", {"name" : "state"}):
            state = tokenInput.get("value", "")                
        return token, state


log = Logger().createLogger()
browser = Browser(log)

with open("config.yaml", "r",  encoding='utf-8') as f:
    config = yaml.safe_load(f)
    username = config["username"]
    password = config["password"]

if browser.login(username, password):
    log.info("Successfully logged in")
    while True:
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            browser.stopMaintaininingSession()
            break
else:
    log.error("Login FAILED")
