import string


from dataclasses import dataclass


@dataclass
class Match:
    tournamentId: str
    league: str
    streamChannel: str
    streamSource: str
