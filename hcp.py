import json
from logger import log
from definitions import BASE_DIR
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Round, Player, Base

engine = create_engine('sqlite:///golfrounds.db', echo=True)
Base.metadata.create_all(engine)

class MyGit:

    def __init__(self, hcp=None, **kwargs):

        self.hcp = hcp
        self.player = None

        if kwargs:
            self.get_player(**kwargs)
        elif hcp is not None:
            log.info(f"Instantiate object with hcp={hcp}")
        else:
            log.error("Class instantiated with hcp=None and kwargs={}")
            raise Exception("Either a handicap or a player must be specified")


    def __repr__(self):
        return f"Hcp(hcp={self.hcp})"


    def get_course_info(self, course):
        with open(BASE_DIR / "slopes.json") as f:
            info = json.load(f)
        
        if not course in info.keys():
            log.error(f"Golf course {course} not in slopes.json")
            return None

        course_info = info[course]
        return {key: course_info[key] for key in course_info}


    def find_shcp(self, course, tee='yellow'):
        """
        Get the given golf course SHCP for the player.
        """

        # Load slope table
        with open(BASE_DIR / "slopes.json") as f:
            slopes = json.load(f)

        try:
            course_info = self.get_course_info(course)
            slope = course_info[f'slope_{tee}']
        except:
            log.error(f"Could not get slope table from slopes.json for course={course} and tee={tee}")
            return None
        
        for shcp, hcp in slope.items():
            if self.hcp >= hcp[0] and self.hcp <= hcp[1]:
                return int(shcp)
        
        # In case wrong hcp is provided in arg
        return None

    
    def calc_bruttoscore_hcp(self, course, score, pcc=0):
        """
        Calculate handicap result from a round with brutto score
        """
        info = self.get_course_info(course)
        return 113/info['slope_rating'] * (score, - info['course_rating'] - pcc)

    
    def calc_stableford_hcp(self, course, points, pcc=0, tee='yelllow'):
        """
        Poängbogey in swedish.
        Calculate handicatp result from a round with stableford score.
        """
        info = self.get_course_info(course)
        shcp = self.find_shcp(course, tee=tee)
        return 113/info['slope_rating'] * (info['par'] + shcp - (points - 36) - info['course_rating'] - pcc)


    def get_hcp(self):
        """
        Reads all rounds from the database and calculates the current exact handicap
        """
        pass


    def update_hcp(self):
        """
        
        """
        pass

    
    @staticmethod
    def add_player(firstname, lastname, hcp, golfid):
        new_player = Player(firstname=firstname, lastname=lastname, hcp=hcp, golfid=golfid)
        with Session(engine) as session:
            session.add(new_player)
            session.commit()

    
    def get_player(self, **kwargs):
        """
        Allowed kwargs:
        id [integer]
        firstname [string]
        lastname [string]
        golfid [string]
        hcp [float]
        """
        with Session(engine) as session:
            player = session.query(Player).filter_by(**kwargs).first()
            if player:
                self.hcp = player.hcp
                self.player = player
            else:
                return None


    def log_round(self, game_type, score, tee):
        """
        1. Calculate hcp result
        2. Add round with hcp result to database
        3. Update hcp
        """
        pass