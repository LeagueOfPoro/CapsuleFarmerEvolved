import requests

from Exceptions.NoAccessTokenException import NoAccessTokenException
from Exceptions.RateLimitException import RateLimitException
from Match import Match
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep, time
from Config import Config
from Exceptions.StatusCodeAssertException import StatusCodeAssertException
import pickle
from pathlib import Path
import jwt


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
            debug=config.get_account(account).get("debug", False))
        self.log = log
        self.config = config
        self.currentlyWatching = {}
        self.liveMatches = {}
        self.account = account

    def login(self, username: str, password: str, refresh_lock) -> bool:
        """
        Login to the website using given credentials. Obtain necessary tokens.

        :param username: string, username of the account
        :param password: string, password of the account
        :param refresh_lock: lock TODO: document param
        :return: boolean, login successful or not
        """
        # Get necessary cookies from the main page
        self.client.get(
            "https://login.leagueoflegends.com/?redirect_uri=https://lolesports.com/&lang=en")
        self.__load_cookies()
        try:
            refresh_lock.acquire()
            # Submit credentials
            data = {"type": "auth", "username": username,
                    "password": password, "remember": True, "language": "en_US"}
            res = self.client.put(
                "https://auth.riotgames.com/api/v1/authorization", json=data)
            if res.status_code == 429:
                retry_after = res.headers['Retry-after']
                raise RateLimitException(retry_after)

            res_json = res.json()
            if "multifactor" in res_json.get("type", ""):
                two_factor_code = input(f"Enter 2FA code for {self.account}:\n")
                print("Code sent")
                data = {"type": "multifactor", "code": two_factor_code, "rememberDevice": True}
                res = self.client.put(
                    "https://auth.riotgames.com/api/v1/authorization", json=data)
                res_json = res.json()
            # Finish OAuth2 login
            res = self.client.get(res_json["response"]["parameters"]["uri"])
        except KeyError:
            return False
        finally:
            refresh_lock.release()
        # Login to lolesports.com, riotgames.com, and playvalorant.com
        token, state = self.__get_login_tokens(res.text)
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
                "https://auth.riotgames.com/authorize?client_id=esports-rna-prod&redirect_uri=https://account.rewards.lolesports.com/v1/session/oauth-callback&response_type=code&scope=openid&prompt=none&state=https://lolesports.com/?memento=na.en_GB",
                allow_redirects=True)

            # Get access and entitlement tokens for the first time
            headers = {"Origin": "https://lolesports.com",
                       "Referrer": "https://lolesports.com"}

            # This requests sometimes returns 404
            res_access_token = self.client.get(
                "https://account.rewards.lolesports.com/v1/session/token", headers=headers)
            # Currently unused but the call might be important server-side
            _ = self.client.get(
                "https://account.rewards.lolesports.com/v1/session/clientconfig/rms", headers=headers)
            if res_access_token.status_code == 200:
                # self.maintainSession()
                self.__dump_cookies()
                return True
        return False

    def refresh_session(self):
        """
        Refresh access and entitlement tokens
        """
        headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com"}
        res_access_token = self.client.get(
            "https://account.rewards.lolesports.com/v1/session/refresh", headers=headers)
        if res_access_token.status_code == 200:
            self.maintain_session()
            self.__dump_cookies()
        else:
            self.log.error("Failed to refresh session")
            raise StatusCodeAssertException(200, res_access_token.status_code, res_access_token.request.url)

    def maintain_session(self):
        """
        Periodically maintain the session by refreshing the access_token
        """
        if self.__needs_session_refresh():
            self.log.debug("Refreshing session.")
            self.refresh_session()

    def get_live_matches(self):
        """
        Retrieve data about currently live matches and store them.
        """
        headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com",
                   "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = self.client.get(
            "https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)
        if res.status_code != 200:
            raise StatusCodeAssertException(200, res.status_code, res.request.url)
        res_json = res.json()
        self.liveMatches = {}
        try:
            events = res_json["data"]["schedule"].get("events", [])
            for event in events:
                tournament_id = event["tournament"]["id"]
                if tournament_id not in self.liveMatches:
                    league = event["league"]["name"]
                    if len(event["streams"]) > 0:
                        stream_channel = event["streams"][0]["parameter"]
                        stream_source = event["streams"][0]["provider"]
                        for stream in event["streams"]:
                            if stream["parameter"] in self.config.bestStreams:
                                stream_channel = stream["parameter"]
                                stream_source = stream["provider"]
                                break
                        self.liveMatches[tournament_id] = Match(
                            tournament_id, league, stream_channel, stream_source)
        except (KeyError, TypeError):
            self.log.error("Could not get live matches")

    def send_watch_to_live(self):
        """
        Send watch event for all the live matches
        """
        drops_available = {}
        for tid in self.liveMatches:
            res = self.__send_watch(self.liveMatches[tid])
            self.log.debug(
                f"{self.account} - {self.liveMatches[tid].league}: {res.json()}")
            if res.json()["droppability"] == "on":
                drops_available[self.liveMatches[tid].league] = True
            else:
                drops_available[self.liveMatches[tid].league] = False
        return drops_available

    def check_new_drops(self, last_check_time):
        try:
            headers = {"Origin": "https://lolesports.com",
                       "Referrer": "https://lolesports.com",
                       "Authorization": "Cookie access_token"}
            res = self.client.get(
                "https://account.service.lolesports.com/fandom-account/v1/earnedDrops?locale=en_GB&site=LOLESPORTS",
                headers=headers)
            res_json = res.json()
            return [drop for drop in res_json if last_check_time <= drop["unlockedDateMillis"]]
        except (KeyError, TypeError):
            self.log.debug("Drop check failed")
            return []

    def __needs_session_refresh(self) -> bool:
        if "access_token" not in self.client.cookies.get_dict():
            raise NoAccessTokenException()

        res = jwt.decode(self.client.cookies.get_dict()["access_token"], options={"verify_signature": False})
        time_left = res['exp'] - int(time())
        self.log.debug(f"{time_left} s until session expires.")
        if time_left < 600:
            return True
        return False

    def __send_watch(self, match: Match) -> requests.Response:
        """
        Sends watch event for a match

        :param match: Match object
        :return: object, response of the request
        """
        data = {"stream_id": match.streamChannel,
                "source": match.streamSource,
                "stream_position_time": datetime.utcnow().isoformat(sep='T', timespec='milliseconds') + 'Z',
                "geolocation": {"code": "CZ", "area": "EU"},
                "tournament_id": match.tournamentId}
        headers = {"Origin": "https://lolesports.com",
                   "Referrer": "https://lolesports.com"}
        res = self.client.post(
            "https://rex.rewards.lolesports.com/v1/events/watch", headers=headers, json=data)
        if res.status_code != 201:
            raise StatusCodeAssertException(201, res.status_code, res.request.url)
        return res

    @staticmethod
    def __get_login_tokens(form: str) -> tuple[str, str]:
        """
        Extract token and state from login page html

        :param form: string, html of the login page
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

    def __dump_cookies(self):
        with open(f'./sessions/{self.account}.saved', 'wb') as f:
            pickle.dump(self.client.cookies, f)

    def __load_cookies(self):
        if Path(f'./sessions/{self.account}.saved').exists():
            with open(f'./sessions/{self.account}.saved', 'rb') as f:
                self.client.cookies.update(pickle.load(f))
                return True
        return False
