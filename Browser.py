from Match import Match
import cloudscraper
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime
import threading
from time import sleep
from Config import Config


class Browser:
    SESSION_REFRESH_INTERVAL = 1800.0
    STREAM_WATCH_INTERVAL = 60.0

    def __init__(self, log, config: Config, account: str):
        """
        Initialize the Browser class

        :param log: log variable
        :param config: Config class object
        :param account: account string
        """
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=config.getAccount(account).get("debug", False))
        self.log = log
        self.config = config
        self.currentlyWatching = {}
        self.liveMatches = {}
        self.account = account

    def login(self, username: str, password: str) -> bool:
        """
        Login to the website using given credentials. Obtain necessary tokens.

        :param username: string, username of the account
        :param password: string, password of the account
        :return: boolean, login successful or not
        """
        # Get necessary cookies from the main page
        self.client.get(
            "https://login.leagueoflegends.com/?redirect_uri=https://lolesports.com/&lang=en")

        # Submit credentials
        data = {"type": "auth", "username": username,
                "password": password, "remember": True, "language": "en_US"}
        res = self.client.put(
            "https://auth.riotgames.com/api/v1/authorization", json=data)
        resJson = res.json()
        try:
            # Finish OAuth2 login
            res = self.client.get(resJson["response"]["parameters"]["uri"])
        except KeyError:
            return False
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

            res = self.client.get(
                "https://auth.riotgames.com/authorize?client_id=esports-rna-prod&redirect_uri=https://account.rewards.lolesports.com/v1/session/oauth-callback&response_type=code&scope=openid&prompt=none&state=https://lolesports.com/?memento=na.en_GB", allow_redirects=True)

            # Get access and entitlement tokens for the first time
            headers = {"Origin": "https://lolesports.com",
                        "Referrer": "https://lolesports.com"}

            # This requests sometimes returns 404
            for i in range(5):
                resAccessToken = self.client.get(
                    "https://account.rewards.lolesports.com/v1/session/token", headers=headers)
                if resAccessToken.status_code == 200:
                    break
                else:
                    sleep(1)

            # Currently unused but the call might be important server-side
            resPasToken = self.client.get(
                "https://account.rewards.lolesports.com/v1/session/clientconfig/rms", headers=headers)
            if resAccessToken.status_code == 200:
                self.maintainSession()
                return True
        return False

    def refreshTokens(self):
        """
        Refresh access and entitlement tokens
        """
        headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com"}
        resAccessToken = self.client.get(
            "https://account.rewards.lolesports.com/v1/session/refresh", headers=headers)
        if resAccessToken.status_code == 200:
            self.maintainSession()
        else:
            self.log.error("Failed to refresh session")

    def maintainSession(self):
        """
        Periodically maintain the session by refreshing the tokens
        """
        self.refreshTimer = threading.Timer(
            Browser.SESSION_REFRESH_INTERVAL, self.refreshTokens)
        self.refreshTimer.start()

    def stopMaintaininingSession(self):
        """
        Stops refreshing the tokens
        """
        self.refreshTimer.cancel()

    def getLiveMatches(self):
        """
        Retrieve data about currently live matches and store them.
        """
        headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com",
                   "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = self.client.get(
            "https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)
        resJson = res.json()
        self.liveMatches = {}
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
                        self.liveMatches[tournamentId] = Match(
                            tournamentId, league, streamChannel, streamSource)
        except (KeyError, TypeError):
            self.log.error("Could not get live matches")

    def sendWatchToLive(self):
        """
        Send watch event for all the live matches
        """
        dropsAvailable = {}
        for tid in self.liveMatches:
            res = self.__sendWatch(self.liveMatches[tid])
            self.log.debug(
                f"{self.account} - {self.liveMatches[tid].league}: {res.json()}")
            if res.json()["droppability"] == "on":   
                dropsAvailable[self.liveMatches[tid].league] = True
            else:
                dropsAvailable[self.liveMatches[tid].league] = False
        return dropsAvailable

    def __sendWatch(self, match: Match) -> object:
        """
        Sends watch event for a match

        :param match: Match object
        :return: object, response of the request
        """
        data = {"stream_id": match.streamChannel,
                "source": match.streamSource,
                "stream_position_time": datetime.utcnow().isoformat(sep='T', timespec='milliseconds')+'Z',
                "geolocation": {"code": "CZ", "area": "EU"},
                "tournament_id": match.tournamentId}
        headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com"}
        return self.client.post(
            "https://rex.rewards.lolesports.com/v1/events/watch", headers=headers, json=data)

    def __getLoginTokens(self, form: str) -> tuple[str, str]:
        """
        Extract token and state from login page html

        :param html: string, html of the login page
        :return: tuple, token and state
        """
        page = BeautifulSoup(form, features="html.parser")
        token = None
        state = None
        if tokenInput := page.find("input", {"name": "token"}):
            token = tokenInput.get("value", "")
        if tokenInput := page.find("input", {"name": "state"}):
            state = tokenInput.get("value", "")
        return token, state
