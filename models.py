import datetime
from sqlalchemy import Column, Integer, Enum, DateTime, Float, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Round(Base):
    __tablename__ = "golfround"

    id = Column(Integer, primary_key=True)
    course = Column(String, nullable=False)
    holes = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    points = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    hcp_result = Column(Float, nullable=False)
    player_id = Column(Integer, ForeignKey('player.id'))
    handicap = relationship('Handicap', cascade="all,delete", backref='player')

    def __repr__(self):
        return f"Round(course={self.course}, hcp={self.hcp_result}, id={self.id})"


class Handicap(Base):
    __tablename__ = "handicap"

    id = Column(Integer, primary_key=True)
    hcp_exact = Column(Float, nullable=False)
    exceptional_adjust = Column(Integer, default=0, nullable=False)
    round_id = Column(Integer, ForeignKey("golfround.id"))

    def __repr__(self):
        return f"<Round id: {self.round_id}, Handicap(hcp_exact={self.hcp_exact}, id={self.id})>"


class Player(Base):
    __tablename__ = "player"

    enums = ("inactive", "soft", "hard")

    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    golfid = Column(String, nullable=False, unique=True)
    hcp = Column(Float, default=54, nullable=False)
    cap = Column(Enum(*enums), default="inactive", nullable=False)
    golfround = relationship('Round', cascade="all,delete", backref='player')

    def __repr__(self):
        return f"Player(firstname={self.firstname}, lastname={self.lastname}, golfid={self.golfid}, hcp={self.hcp}, id={self.id})"