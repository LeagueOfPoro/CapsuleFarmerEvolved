from Config import Config
from Match import Match
from Logger.Logger import Logger
import cloudscraper
import asyncio
from pprint import pprint
from bs4 import BeautifulSoup
import yaml
import logging
from datetime import timedelta, datetime
import time
import threading


class Browser:
    SESSION_REFRESH_INTERVAL = 1800.0
    STREAM_WATCH_INTERVAL = 60.0

    def __init__(self, log, config):
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=True)
        self.log = log
        self.config = config
        self.currentlyWatching = {}
        self.liveMatches = {}

    # Initial login
    def login(self, username, password):
        # Get necessary cookies from the main page
        self.client.get(
            "https://login.leagueoflegends.com/?redirect_uri=https://lolesports.com/&lang=en")

        # Submit credentials
        data = {"type": "auth", "username": username,
                "password": password, "remember": True, "language": "en_US"}
        res = self.client.put(
            "https://auth.riotgames.com/api/v1/authorization", json=data)
        resJson = res.json()
        if resJson.get("type", "") and resJson["response"].get("parameters", "") and resJson["response"]["parameters"].get("uri", ""):
            # Finish OAuth2 login
            res = self.client.get(resJson["response"]["parameters"]["uri"])

            # Login to lolesports.com, riotgames.com, and playvalorant.com
            token, state = self.__getLoginTokens(res.text)
            if token and state:
                data = {"token": token, "state": state}
                self.client.post(
                    "https://login.riotgames.com/sso/login", data=data)
                self.client.post(
                    "https://login.lolesports.com/sso/login", data=data)
                self.client.post(
                    "https://login.playvalorant.com/sso/login", data=data)

                res = self.client.post(
                    "https://login.leagueoflegends.com/sso/callback", data=data)

                # Get access and entitlement tokens for the first time
                headers = {"Origin": "https://lolesports.com",
                           "Referrer": "https://lolesports.com"}
                resAccessToken = self.client.get(
                    "https://account.rewards.lolesports.com/v1/session/token", headers=headers)
                resEntitlementToken = self.client.get(
                    "https://entitlements.rewards.lolesports.com/v1/entitlements/?token=true", headers=headers)
                resPasToken = self.client.get(
                    "https://account.rewards.lolesports.com/v1/session/clientconfig/rms", headers=headers)
                if resAccessToken.status_code == 200 and resEntitlementToken.status_code == 200:
                    self.maintainSession()
                    return True
        return False

    # Refresh access and entitlement tokens
    def refreshTokens(self):
        headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com"}
        resAccessToken = self.client.get(
            "https://account.rewards.lolesports.com/v1/session/refresh", headers=headers)
        resEntitlementToken = self.client.get(
            "https://entitlements.rewards.lolesports.com/v1/entitlements/?token=true", headers=headers)
        if resAccessToken.status_code == 200 and resEntitlementToken.status_code == 200:
            self.maintainSession()
        else:
            self.log.error("Failed to refresh session")

    def maintainSession(self):
        self.refreshTimer = threading.Timer(
            Browser.SESSION_REFRESH_INTERVAL, self.refreshTokens)
        self.refreshTimer.start()

    def stopMaintaininingSession(self):
        self.refreshTimer.cancel()

    def getLiveMatches(self):
        headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com",
                   "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = self.client.get(
            "https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)
        resJson = res.json()
        try:
            events = resJson["data"]["schedule"].get("events", [])
            for event in events:
                tournamentId = event["tournament"]["id"]
                if tournamentId not in self.liveMatches:
                    league = event["league"]["name"]
                    if len(event["streams"]) > 0:
                        streamChannel = event["streams"][0]["parameter"]
                        streamSource = event["streams"][0]["provider"]
                        for stream in event["streams"]:
                            if stream["parameter"] in self.config.bestStreams:
                                streamChannel = stream["parameter"]
                                streamSource = stream["provider"]
                                break
                        self.liveMatches[tournamentId] = Match(tournamentId, league, streamChannel, streamSource)
        except (KeyError, TypeError):
            log.error("Could not get live matches")
    
    def startWatchingNewMatches(self):
        for tid in self.liveMatches:
            if tid not in self.currentlyWatching:
                self.watch(self.liveMatches[tid])

    def watch(self, match: Match):
        self.currentlyWatching[match.tournamentId] = threading.Timer(
            Browser.STREAM_WATCH_INTERVAL, self.__sendWatch, [match])
        self.currentlyWatching[match.tournamentId].start()

    def stopWatching(self, tournamentId):
        t = self.currentlyWatching.get(tournamentId, None)
        if t:
            t.cancel()

    def stopWatchingAll(self):
        for t in self.currentlyWatching.values():
            t.cancel()
    
    def cleanUpWatchlist(self):
        removed = []
        for tid in self.currentlyWatching:
            if tid not in self.liveMatches:
                self.stopWatching(tid)
                removed.append(tid)

        for tid in removed:
            self.currentlyWatching.pop(tid)        

    def __sendWatch(self, match: Match):
        data = {"stream_id": match.streamChannel,
                "source": match.streamSource,
                "stream_position_time": datetime.utcnow().isoformat(sep='T', timespec='milliseconds')+'Z',
                "geolocation": {"code": "CZ", "area": "EU"},
                "tournament_id": match.tournamentId}
        headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com"}
        self.client.post(
            "https://rex.rewards.lolesports.com/v1/events/watch", headers=headers, json=data)
        self.watch(match)

    def __getLoginTokens(self, form):
        page = BeautifulSoup(form, features="html.parser")
        token = None
        state = None
        if tokenInput := page.find("input", {"name": "token"}):
            token = tokenInput.get("value", "")
        if tokenInput := page.find("input", {"name": "state"}):
            state = tokenInput.get("value", "")
        return token, state


log = Logger().createLogger()
config = Config()
browser = Browser(log, config)

if browser.login(config.username, config.password):
    log.info("Successfully logged in")
    while True:
        try:
            log.debug("Beat")
            browser.getLiveMatches()
            browser.cleanUpWatchlist()
            browser.startWatchingNewMatches()
            time.sleep(60)
        except KeyboardInterrupt:
            browser.stopMaintaininingSession()
            browser.stopWatchingAll()
            break
else:
    log.error("Login FAILED")
