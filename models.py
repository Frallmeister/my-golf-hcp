import datetime
from sqlalchemy import Column, Integer, Enum, DateTime, Float, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Round(Base):
    __tablename__ = "golfrounds"

    id = Column(Integer, primary_key=True)
    course = Column(String, nullable=False)
    hcp_result = Column(Float, nullable=False)
    hcp_exact = Column(Float, nullable=False)
    holes = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    points = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    exceptional_adjust = Column(Integer, default=0, nullable=False)
    player_id = Column(Integer, ForeignKey('player.id'))

    def __repr__(self):
        return f"Round(course={self.course}, hcp={self.hcp}, id={self.id})"


class Player(Base):
    __tablename__ = "player"

    enums = ("inactive", "soft", "hard")

    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    golfid = Column(String, nullable=False, unique=True)
    hcp = Column(Float, default=54, nullable=False)
    cap = Column(Enum(*enums), default="inactive", nullable=False)
    golfrounds = relationship('Round', cascade="all,delete", backref='player')

    def __repr__(self):
        return f"Player(firstname={self.firstname}, lastname={self.lastname}, golfid={self.golfid}, hcp={self.hcp}, id={self.id})"