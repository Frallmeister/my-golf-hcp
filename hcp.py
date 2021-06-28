import json
import datetime
from logger import log
from definitions import BASE_DIR, playerselected
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import numpy as np
from models import Round, Player, Handicap, Base

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
        log.debug(f"shcp = {shcp}")

        # Add points for holes not played
        points += 2*(len(info['holes_par']) - holes)
        if holes < 9:
            log.error("Logging fewer than 9 holes is not allowed")
            return None
        elif holes < 14:
            points -= 1
            
        if shcp is not None:
            return min(54, round(113/info['slope_rating'] * (info['par'] + shcp - (points - 36) - info['course_rating'] - pcc), 1))
        else:
            return None


    @playerselected
    def get_exact_hcp(self):
        """
        Reads all rounds from the database and calculates the current exact handicap
        Both Cap and Exceptional score is applied.

        None will be returned if no rounds are logged.

        Returns:
            exact_hcp: The new exact hcp with cap and exceptional score applied.
            cap_status: (str: inactive, soft, hard) Describes the applied cap
            exceptional_score: (int: 0, -1, -2) Describes the applied exceptional score 
        """
        cap_status = None
        with Session(engine) as session:
            played_rounds = session.query(Round).order_by(Round.id.desc()).limit(20).all()
        
        if not played_rounds:
            log.warning("No registred rounds")
            return None

        n_rounds = len(played_rounds)
        results = sorted([r.hcp_result for r in played_rounds])

        # Apply exceptional score
        last_result = played_rounds[-1].hcp_result
        if last_result <= self.player.hcp - 10.0:
            exceptional_score = -2
        elif last_result <= self.player.hcp - 7.0:
            exceptional_score = -1
        else:
            exceptional_score = 0
        results = [r + exceptional_score for r in results]

        # Calculate exact hcp from hcp table
        if n_rounds <= 3:
            exact_hcp = round(min(results) - 2, 1)
        elif n_rounds == 4:
            exact_hcp = round(min(results) - 1, 1)
        elif n_rounds == 5:
            exact_hcp = round(min(results), 1)
        elif n_rounds == 6:
            exact_hcp = round(np.mean(results[:2]) - 1, 1)
        elif n_rounds <= 8:
            exact_hcp = round(np.mean(results[:2]), 1)
        elif n_rounds <= 11:
            exact_hcp = round(np.mean(results[:3]), 1)
        elif n_rounds <= 14:
            exact_hcp = round(np.mean(results[:4]), 1)
        elif n_rounds <= 16:
            exact_hcp = round(np.mean(results[:5]), 1)
        elif n_rounds <= 18:
            exact_hcp = round(np.mean(results[:6]), 1)
        elif n_rounds <= 19:
            exact_hcp = round(np.mean(results[:7]), 1)
        elif n_rounds == 20:
            exact_hcp = round(np.mean(results[:8]), 1)
            # Run cap function
            log.debug(f"exact_hcp before cap = {exact_hcp}")
            exact_hcp, cap_status = self.cap_hcp(exact_hcp, self.player.hcp)
            log.debug(f"exact_hcp after cap = {exact_hcp}")

        return (exact_hcp, cap_status, exceptional_score)


    @staticmethod
    def cap_hcp(new_hcp, current_hcp):
        """
        Takes a new hcp and the current hcp and calculates a cap of the new hcp.
        Returns:
            capped_hcp: [float] The calculated hcp.
            cap_status: [str: soft, hard] The type of cap that is applied if any. Return None in case of no change.
        """

        # Get rounds and the lowest exact handicap last 12 months
        with Session(engine) as session:
            rounds = session.query(Round).order_by(Round.date.desc()).all()

            latest_date = rounds[-1].date
            dt = datetime.timedelta(days=365)
            start_date = latest_date - dt
            lowest_hcp = min([r.handicap[0].hcp_exact for r in rounds[1:] if r.date > start_date])

        # Cap can only be enabled when more than 20 rounds have been registred
        n_rounds = len(rounds)
        if n_rounds < 20:
            log.warning("Calling cap() with fewer than 20 rounds")
            raise Exception(f"At least 20 rounds are required to enable cap. Only {n_rounds} are registred.")

        if new_hcp <= lowest_hcp + 3.0:
            return new_hcp, None

        log.info(f"Capping hcp {new_hcp} from lowest exact hcp {lowest_hcp} when current hcp is {current_hcp}")

        hcp_add = 3.0 + (new_hcp - (lowest_hcp + 3.0))/2
        # hcp_add = round(hcp_add, 1)

        cap_status = 'hard' if hcp_add > 7 else 'soft'
        capped_hcp = round(lowest_hcp + min(hcp_add, 7.0), 1)
        log.debug(f"Obtained new capped hcp {capped_hcp}, cap_status={cap_status}")
        return capped_hcp, cap_status


    @playerselected
    def update_hcp(self):
        """
        Update players exact hcp,
        Update players cap status,
        Insert Handicap record
        """
        player_id = self.player.id
        temp = self.get_exact_hcp()
        if temp is None:
            return None
        else:
            exact_hcp, cap_status, exceptional_score = temp

        log.debug(f"Calculated new exact hcp {exact_hcp}")

        # Insert handicap record and update player exact hcp
        with Session(engine) as session:
            rounds = session.query(Round).order_by(Round.date.desc()).limit(20).all()
            handicap = Handicap(hcp_exact=exact_hcp, exceptional_adjust=exceptional_score, round_id=rounds[0].id)
            self.player.hcp = exact_hcp
            
            session.add(handicap)
            session.add(self.player)
            session.commit()
            log.info(f"Inserted {handicap} to database and updated {self.player} with hcp={exact_hcp}")
            
        self.get_player(id=player_id)

    
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
                log.info(f"Assigned player to instance {player}")
                self.player = player
            else:
                return None


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
            raise Exception(f"Unexpected game_type provided. Received '{game_type}'")
        
        # In case None was returned in round_hcp_result
        if round_hcp_result is None:
            log.error("Round hcp could not be calculated")
            return None

        # Create a dictionary with data to insert in the db
        round_data = dict(
            course = course,
            holes = holes,
            hcp_result = round_hcp_result,
            player_id = player_id
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

        # Update exact hcp for the player
        self.update_hcp()


if __name__ == '__main__':
    obj = MyGit()
    obj.get_player(golfid='900828-008')
    exact_hcp = obj.get_exact_hcp()
    import random
    # obj.log_round("orust", "stableford", holes=18, points=random.randint(33, 38))