import string


from dataclasses import dataclass


@dataclass
class Match:
    tournamentId: string
    league: string
    streamChannel: string
    streamSource: string
