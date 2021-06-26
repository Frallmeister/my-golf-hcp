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

    
    def calc_bruttoscore_hcp(self, course, shots, pcc=0):
        """
        Calculate handicap result from a round with brutto score
        course: [string]
        shots: [dict]
        pcc: [int]
        """
        info = self.get_course_info(course)
        n_holes = len(shots)
        
        # Calculate brutto score
        bruttoscore = sum(shots.values())
        holes_par = info['holes_par']
        # Add par for holes not played to brutto score
        bruttoscore += sum([holes_par[i] for i in range(len(holes_par)) if i+1 not in shots.keys()])

        if n_holes < 9:
            log.error("Logging fewer than 9 holes is not allowed")
            return None
        elif n_holes < 14:
            bruttoscore += 1
        return min(54, round(113/info['slope_rating'] * (bruttoscore - info['course_rating'] - pcc), 1))

    
    def calc_stableford_hcp(self, course, hcp, points, holes, pcc=0, tee='yellow'):
        """
        Poängbogey in swedish.
        Calculate handicatp result from a round with stableford score.
        course: [string]
        hcp: [float]
        points: [int]
        holes: [int]
        pcc: [int]
        tee: [string]
        """
        info = self.get_course_info(course)
        shcp = self.find_shcp(course, hcp, tee=tee)

        # Add points for holes not played
        points += 2*(len(info['holes_par']) - holes)
        if holes < 9:
            log.error("Logging fewer than 9 holes is not allowed")
            return None
        elif holes < 14:
            points -= 1
            
        if shcp:
            return min(54, round(113/info['slope_rating'] * (info['par'] + shcp - (points - 36) - info['course_rating'] - pcc), 1))
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
    def create_player(firstname, lastname, hcp, golfid):
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


    def cap(self):
        pass


    @playerselected
    def log_round(self, course, game_type, holes=None, date=None, points=None, shots=None, tee='yellow', pcc=0):
        """
        course [string]
        game_type [string]: (bruttoscore, stableford)
        holes [int]
        date [datetime.date]
        points [int]
        shots [int, dict]
        tee [string]
        pcc [int]
        """
        current_hcp = self.player.hcp
        player_id = self.player.id

        # Calculate handicap result from the round
        if game_type == "bruttoscore":
            if isinstance(shots, dict) != True:
                raise Exception("shots must be a dict type for game_type=bruttoscore")
            round_hcp_result = self.calc_bruttoscore_hcp(course=course, shots=shots, pcc=pcc)
            holes = len(shots)
            shots = sum(shots.values())

        elif game_type == "stableford":
            if points is None:
                raise Exception("points must be an integer when game_type=stableford, received points=None")
            if isinstance(shots, dict):
                holes = len(shots)
                shots = sum(shots.values())
            elif isinstance(holes, int) != True:
                raise Exception(f"holes must be an integer if shots is not a dict, received {type(holes).__name__}")

            round_hcp_result = self.calc_stableford_hcp(course=course, hcp=current_hcp, points=points, holes=holes, pcc=pcc, tee=tee)
        else:
            raise Exception("Unexpected game_type provided")
        
        # In case None was returned in round_hcp_result
        if round_hcp_result is None:
            log.error("Round hcp could not be calculated")
            return None

        # Create a dictionary with data to insert in the db
        round_data = dict(
            course = course,
            holes = holes,
            player_id = player_id,
            hcp = round_hcp_result,
        )

        # Add kwargs that are not None to the Round entry
        kwargs = {'date': date, 'points': points, 'shots': shots}
        optional_cols = {k: v for k, v in kwargs.items() if v is not None}
        round_data.update(optional_cols)

        # Insert a new round in the database
        new_round = Round(**round_data)
        with Session(engine) as session:
            session.add(new_round)
            session.commit()
            log.info(f"Successfully added new round, {new_round}")



if __name__ == '__main__':
    obj = MyGit()
    obj.get_player(golfid='900828-008')
    h2=obj.calc_stableford_hcp('orust', hcp=19.1, points=36, holes=10)