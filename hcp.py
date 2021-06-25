import json
from logger import log
import sqlalchemy as db
from models import Rounds, Base

engine = db.create_engine('sqlite:///golfrounds.db', echo=True)
Base.metadata.create_all(engine)

class Player:

    def __init__(self, hcp):
        self.hcp = hcp
        log.info(f"Instantiate Player object with hcp={hcp}")

    def __repr__(self):
        return f"Player(hcp={self.hcp})"

    def find_shcp(self, course, tee='yellow'):
        """
        Get the given golf course SHCP for the player.
        """

        # Load slope table
        with open("slopes.json") as f:
            slopes = json.load(f)

        try:
            slope = slopes[course.lower()][f'slope_{tee}']
        except:
            log.error(f"Could not get slope table from slopes.json for course={course} and tee={tee}")
            return None
        
        for shcp, hcp in slope.items():
            if self.hcp >= hcp[0] and self.hcp <= hcp[1]:
                return int(shcp)
        
        # In case wrong hcp is provided in arg
        return None