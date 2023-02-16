class SharedData:
    def __init__(self) -> None:
        self.liveMatches = {}
        self.timeUntilNextMatch = "None"
    
    def setLiveMatches(self, liveMatches):
        self.liveMatches = liveMatches

    def getLiveMatches(self):
        return self.liveMatches

    def setTimeUntilNextMatch(self, timeUntilNextMatch):
        self.timeUntilNextMatch = timeUntilNextMatch

    def addTimeUntilNextMatch(self, timeUntilNextMatch):
        self.timeUntilNextMatch += "\n" + timeUntilNextMatch

    def getTimeUntilNextMatch(self):
        return self.timeUntilNextMatch