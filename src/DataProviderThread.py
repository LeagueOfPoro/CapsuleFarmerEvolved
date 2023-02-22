from datetime import datetime, timezone, timedelta
from threading import Thread
from time import sleep
import cloudscraper

from AssertCondition import AssertCondition
from Config import Config
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
        self.currentTime = None
        self.startTime = None

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
                   "x-api-key": Config.RIOT_API_KEY}
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
                   "x-api-key": Config.RIOT_API_KEY}
        try:
            res = self.client.get(
                "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB", headers=headers)
            AssertCondition.statusCodeMatches(200, res)
            resJson = res.json()
            res.close()
            events = resJson["data"]["schedule"]["events"]
            for event in events:
                if event["state"] == "unstarted":
                    if self._isStartTimeLater(event["startTime"]):  # startTime is later
                        timeDiff = self._calculateTimeDifference(event["startTime"])
                        systemTimeDT = self._getSystemTime()

                        #  This line calculates a timezone-correct startime no matter which timezone you're in
                        startTime = systemTimeDT + timeDiff

                        niceStartTime = datetime.strftime(startTime, '%H:%M')
                        self.sharedData.setTimeUntilNextMatch(
                            f"Up next: {event['league']['name']} at {niceStartTime}")
                        break
                    else:  # We're past the startTime due to delay or cancellation i'm guessing
                        continue  # Continue for loop to find next 'unstarted' event
        except StatusCodeAssertException as ex:
            self.log.error(ex)
            self.sharedData.setTimeUntilNextMatch("None")
        except Exception as ex:
            self.log.error(ex)
            self.sharedData.setTimeUntilNextMatch("None")

    def _isStartTimeLater(self, time: str) -> bool:
        """
        Checks if an events starttime is greater than the current time

        :param time: string
        :return: bool
        """
        datetimeFormat = '%Y-%m-%dT%H:%M:%SZ'
        self.startTime = datetime.strptime(time, datetimeFormat)
        currentTimeString = datetime.now(timezone.utc).strftime(datetimeFormat)
        self.currentTime = datetime.strptime(currentTimeString, datetimeFormat)
        return self.currentTime < self.startTime

    def _calculateTimeDifference(self, time: str) -> timedelta:
        """
        Calculates the time difference between the current time and a starttime

        :param time: string
        :return: timedelta, timedelta object containing time difference
        """
        datetimeFormat = '%Y-%m-%dT%H:%M:%SZ'
        self.startTime = datetime.strptime(time, datetimeFormat)
        currentTimeString = datetime.now(timezone.utc).strftime(datetimeFormat)
        self.currentTime = datetime.strptime(currentTimeString, datetimeFormat)

        timeDifference = self.startTime - self.currentTime
        return timeDifference

    def _getSystemTime(self) -> datetime:
        """
        Gets the systems current time

        :return: datetime, systems current time as datetime
        """
        datetimeFormat = '%Y-%m-%dT%H:%M:%SZ'
        systemTimeStr = datetime.now().strftime(datetimeFormat)
        systemTimeDT = datetime.strptime(systemTimeStr, datetimeFormat)
        return systemTimeDT
        