from AssertCondition import AssertCondition
from Exceptions.NoAccessTokenException import NoAccessTokenException
from Exceptions.RateLimitException import RateLimitException
from Match import Match
import cloudscraper
from pprint import pprint
from bs4 import BeautifulSoup
from datetime import datetime
import threading
from time import sleep, time
from Config import Config
from Exceptions.StatusCodeAssertException import StatusCodeAssertException
import pickle
from pathlib import Path
import jwt

from SharedData import SharedData


class Browser:
    SESSION_REFRESH_INTERVAL = 1800.0
    STREAM_WATCH_INTERVAL = 60.0

    def __init__(self, log, config: Config, account: str, sharedData: SharedData):
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
            debug=False)
        self.log = log
        self.config = config
        self.currentlyWatching = {}
        self.account = account
        self.sharedData = sharedData

    def login(self, username: str, password: str, refreshLock) -> bool:
        """
        Login to the website using given credentials. Obtain necessary tokens.

        :param username: string, username of the account
        :param password: string, password of the account
        :return: boolean, login successful or not
        """
        # Get necessary cookies from the main page
        self.client.get(
            "https://login.leagueoflegends.com/?redirect_uri=https://lolesports.com/&lang=en")
        self.__loadCookies()
        try:
            refreshLock.acquire()
            # Submit credentials
            data = {"type": "auth", "username": username,
                    "password": password, "remember": True, "language": "en_US"}
            res = self.client.put(
                "https://auth.riotgames.com/api/v1/authorization", json=data)
            if res.status_code == 429:
                retryAfter = res.headers['Retry-after']
                raise RateLimitException(retryAfter)
                
            resJson = res.json()
            if "multifactor" in resJson.get("type", ""):
                twoFactorCode = input(f"Enter 2FA code for {self.account}:\n")
                print("Code sent")
                data = {"type": "multifactor", "code": twoFactorCode, "rememberDevice": True}
                res = self.client.put(
                    "https://auth.riotgames.com/api/v1/authorization", json=data)
                resJson = res.json()
            # Finish OAuth2 login
            res = self.client.get(resJson["response"]["parameters"]["uri"])
        except KeyError:
            return False
        except RateLimitException as ex:
            self.log.error(f"You are being rate-limited. Retry after {ex}")
            return False
        finally:
            refreshLock.release()
        # Login to lolesports.com, riotgames.com, and playvalorant.com
        token, state = self.__getLoginTokens(res.text)
        if token and state:
            data = {"token": token, "state": state}
            self.client.post(
                "https://login.riotgames.com/sso/login", data=data).close()
            self.client.post(
                "https://login.lolesports.com/sso/login", data=data).close()
            self.client.post(
                "https://login.playvalorant.com/sso/login", data=data).close()
            self.client.post(
                "https://login.leagueoflegends.com/sso/callback", data=data).close()
            self.client.get(
                "https://auth.riotgames.com/authorize?client_id=esports-rna-prod&redirect_uri=https://account.rewards.lolesports.com/v1/session/oauth-callback&response_type=code&scope=openid&prompt=none&state=https://lolesports.com/?memento=na.en_GB", allow_redirects=True).close()

            # Get access and entitlement tokens for the first time
            headers = {"Origin": "https://lolesports.com",
                        "Referrer": "https://lolesports.com"}

            # This requests sometimes returns 404
            resAccessToken = self.client.get(
                "https://account.rewards.lolesports.com/v1/session/token", headers=headers)
            # Currently unused but the call might be important server-side
            resPasToken = self.client.get(
                "https://account.rewards.lolesports.com/v1/session/clientconfig/rms", headers=headers).close()
            if resAccessToken.status_code == 200:
                self.__dumpCookies()
                return True
        return False

    def refreshSession(self):
        """
        Refresh access and entitlement tokens
        """
        try:
            headers = {"Origin": "https://lolesports.com",
                    "Referrer": "https://lolesports.com"}
            resAccessToken = self.client.get(
                "https://account.rewards.lolesports.com/v1/session/refresh", headers=headers)
            AssertCondition.statusCodeMatches(200, resAccessToken)
            resAccessToken.close()
            self.__dumpCookies()
        except StatusCodeAssertException as ex:
            self.log.error("Failed to refresh session")
            self.log.error(ex)
            raise ex

    def maintainSession(self):
        """
        Periodically maintain the session by refreshing the access_token
        """
        if self.__needSessionRefresh():
            self.log.debug("Refreshing session.")
            self.refreshSession()

    def sendWatchToLive(self) -> list:
        """
        Send watch event for all the live matches
        """
        watchFailed = []
        for tid in self.sharedData.getLiveMatches():
            try:
                self.__sendWatch(self.sharedData.getLiveMatches()[tid])
            except StatusCodeAssertException as ex:
                self.log.error(f"Failed to send watch heartbeat for {self.sharedData.getLiveMatches()[tid].league}")
                self.log.error(ex)
                watchFailed.append(self.sharedData.getLiveMatches()[tid].league)
        return watchFailed
    
    def checkNewDrops(self, lastCheckTime):
        try:
            headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com",
                   "Authorization": "Cookie access_token"}
            res = self.client.get("https://account.service.lolesports.com/fandom-account/v1/earnedDrops?locale=en_GB&site=LOLESPORTS", headers=headers)
            resJson = res.json()
            res.close()
            return [drop for drop in resJson if lastCheckTime <= drop["unlockedDateMillis"]]
        except (KeyError, TypeError):
            self.log.debug("Drop check failed")
            return []

    def __needSessionRefresh(self) -> bool:
        if "access_token" not in self.client.cookies.get_dict():
            raise NoAccessTokenException()

        res = jwt.decode(self.client.cookies.get_dict()["access_token"], options={"verify_signature": False})
        timeLeft = res['exp'] - int(time())
        self.log.debug(f"{timeLeft} s until session expires.")
        if timeLeft < 600:
            return True
        return False

    def __sendWatch(self, match: Match):
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
        res = self.client.post(
            "https://rex.rewards.lolesports.com/v1/events/watch", headers=headers, json=data)
        AssertCondition.statusCodeMatches(201, res)
        res.close()

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

    def __dumpCookies(self):
        with open(f'./sessions/{self.account}.saved', 'wb') as f:
            pickle.dump(self.client.cookies, f)

    def __loadCookies(self):
        if Path(f'./sessions/{self.account}.saved').exists():
            with open(f'./sessions/{self.account}.saved', 'rb') as f:
                self.client.cookies.update(pickle.load(f))
                return True
        return False
