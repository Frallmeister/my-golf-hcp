from sqlalchemy import Column, Integer, Enum, Date, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Rounds(Base):
    __tablename__ = "golfrounds"

    id = Column(Integer, primary_key=True)
    course = Column(String, nullable=False)
    hcp = Column(Float, nullable=False)
    points = Column(Integer, nullable=False)
    shots = Column(Integer, nullable=False)

    def __repr__(self):
        return f"Shots(course={self.course}, points={self.points}, hcp={self.hcp})"