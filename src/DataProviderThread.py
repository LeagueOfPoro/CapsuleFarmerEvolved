from threading import Thread
from time import sleep
import cloudscraper
from datetime import datetime, timezone
from AssertCondition import AssertCondition
from Exceptions.StatusCodeAssertException import StatusCodeAssertException
from Match import Match
from SharedData import SharedData


class DataProviderThread(Thread):
    """
    A thread that handles data that is shared among all accounts to reduce network load.
    """

    DEFAULT_SLEEP_DURATION = 60.0

    def __init__(self, log, config, sharedData: SharedData):
        super().__init__()
        self.log = log
        self.sharedData = sharedData
        self.config = config
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=False)

    def run(self):
        while True:
            try:
                self.fetchLiveMatches()
                self.fetchTimeUntilNextMatch()
                sleep(DataProviderThread.DEFAULT_SLEEP_DURATION)
            except:
                self.log.error("RIP")

    def fetchLiveMatches(self):
        """
        Retrieve data about currently live matches and store them.
        """
        headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com",
                   "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        res = self.client.get(
            "https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB", headers=headers)
        AssertCondition.statusCodeMatches(200, res)
        resJson = res.json()
        res.close()
        liveMatches = {}
        try:
            events = resJson["data"]["schedule"].get("events", [])
            for event in events:
                tournamentId = event["tournament"]["id"]
                if tournamentId not in liveMatches:
                    league = event["league"]["name"]
                    if len(event["streams"]) > 0:
                        streamChannel = event["streams"][0]["parameter"]
                        streamSource = event["streams"][0]["provider"]
                        for stream in event["streams"]:
                            if stream["parameter"] in self.config.bestStreams:
                                streamChannel = stream["parameter"]
                                streamSource = stream["provider"]
                                break
                        liveMatches[tournamentId] = Match(
                            tournamentId, league, streamChannel, streamSource)
            self.sharedData.setLiveMatches(liveMatches)
        except (KeyError, TypeError):
            self.sharedData.setLiveMatches()
            self.log.error("Could not get live matches")

    def fetchTimeUntilNextMatch(self):
        """
        Retrieve data about currently live matches and store them.
        """
        headers = {"Origin": "https://lolesports.com", "Referrer": "https://lolesports.com",
                   "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
        try:
            res = self.client.get(
                "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB", headers=headers)
            AssertCondition.statusCodeMatches(200, res)
            resJson = res.json()
            res.close()
            events = resJson["data"]["schedule"]["events"]
            for event in events:
                if event["state"] == "unstarted":
                    startTime = datetime.strptime(event["startTime"], '%Y-%m-%dT%H:%M:%SZ')
                    currentTimeString = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                    currentTimeDatetime = datetime.strptime(currentTimeString, '%Y-%m-%dT%H:%M:%SZ')

                    if currentTimeDatetime < startTime:
                        timeUntil = startTime - currentTimeDatetime
                        total_seconds = int(timeUntil.total_seconds())
                        days, remainder = divmod(total_seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        self.sharedData.setTimeUntilNextMatch(
                            f"None - next in {days}d {hours}h" if days else f'None - next in {hours}h {minutes}m')
                    else:
                        self.sharedData.setTimeUntilNextMatch("None - could not determine when next match starts")

                    break
        except StatusCodeAssertException as ex:
            self.log.error(ex)
            self.sharedData.setTimeUntilNextMatch("None")
        except:
            self.sharedData.setTimeUntilNextMatch("None")