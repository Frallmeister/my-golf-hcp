import json
from logger import log
from definitions import BASE_DIR, playerselected
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Round, Player, Base

engine = create_engine('sqlite:///golfrounds.db', echo=False)
Base.metadata.create_all(engine)


class MyGit:
    """
    My version of "Golfens IT-system", my own , my precious...
    """

    def __init__(self, **kwargs):

        self.player = None

        # Check expected kwargs
        if kwargs:
            keys = kwargs.keys()
            p = Player()
            allowed_keys = [column.key for column in p.__table__.columns]
            del p
            for key in keys:
                if key not in allowed_keys:
                    raise Exception(f"Got unexpected key word, {key}")
            
            self.get_player(**kwargs)


    def __repr__(self):
        return f"MyGit(player={self.player})"


    @staticmethod
    def get_course_info(course):
        with open(BASE_DIR / "slopes.json") as f:
            info = json.load(f)
        
        if not course in info.keys():
            log.error(f"Golf course {course} not in slopes.json")
            return None

        course_info = info[course]
        return {key: course_info[key] for key in course_info}


    def find_shcp(self, course, hcp, tee='yellow'):
        """
        Get the given golf course SHCP for the player.
        """

        try:
            course_info = self.get_course_info(course)
            slope = course_info[f'slope_{tee}']
        except:
            log.error(f"Could not get slope table from slopes.json for course={course} and tee={tee}")
            return None
        
        for shcp, hcp_range in slope.items():
            if hcp >= hcp_range[0] and hcp <= hcp_range[1]:
                return int(shcp)
        
        # In case wrong hcp is provided in arg
        return None

    
    def calc_bruttoscore_hcp(self, course, score, pcc=0):
        """
        Calculate handicap result from a round with brutto score
        """
        info = self.get_course_info(course)
        return round(113/info['slope_rating'] * (score - info['course_rating'] - pcc), 1)

    
    def calc_stableford_hcp(self, course, hcp, points, pcc=0, tee='yellow'):
        """
        Poängbogey in swedish.
        Calculate handicatp result from a round with stableford score.
        """
        info = self.get_course_info(course)
        shcp = self.find_shcp(course, hcp, tee=tee)
        if shcp:
            return round(113/info['slope_rating'] * (info['par'] + shcp - (points - 36) - info['course_rating'] - pcc), 1)
        else:
            return None


    @playerselected
    def get_hcp(self):
        """
        Reads all rounds from the database and calculates the current exact handicap
        """
        pass


    @playerselected
    def update_hcp(self):
        """
        Fetches the current hcp from get_hcp() and updates the player hcp in the db
        """
        print("SUCCESS")

    
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


    @playerselected
    def log_round(self, game_type, score, tee):
        """
        1. Calculate hcp result
        2. Add round with hcp result to database
        3. Update hcp
        """
        pass


if __name__ == '__main__':
    obj = MyGit()
    obj.get_player(golfid='900828-008')
    h1=obj.calc_bruttoscore_hcp('orust', 92)
    h2=obj.calc_stableford_hcp('orust', 19.1, 36)