import datetime
from sqlalchemy import Column, Integer, Enum, Date, Float, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Round(Base):
    __tablename__ = "golfrounds"

    id = Column(Integer, primary_key=True)
    course = Column(String, nullable=False)
    hcp = Column(Float, nullable=False)
    holes = Column(Integer, nullable=False)
    date = Column(Date, default=datetime.datetime.utcnow().date)
    points = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    player_id = Column(Integer, ForeignKey('player.id'))

    def __repr__(self):
        return f"Round(course={self.course}, hcp={self.hcp}, id={self.id})"


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    golfid = Column(String, nullable=False, unique=True)
    hcp = Column(Float)
    golfrounds = relationship('Round', cascade="all,delete", backref='player')

    def __repr__(self):
        return f"Player(firstname={self.firstname}, lastname={self.lastname}, golfid={self.golfid}, hcp={self.hcp}"