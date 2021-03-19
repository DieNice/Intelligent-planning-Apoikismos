from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///ipa.db', echo=False)

Base = declarative_base()


class Material(Base):
    __tablename__ = 'material'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Material('%s','%s')>" % (self.name, self.description)


class Instrument(Base):
    __tablename__ = 'instrument'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Instrument('%s','%s')>" % (self.name, self.description)


class Building(Base):
    __tablename__ = 'building'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Building('%s','%s')>" % (self.name, self.description)


class PossibleAction(Base):
    __tablename__ = 'possible_action'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    precondition = relationship("Precondition")
    result = relationship("Result")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Material('%s','%s')>" % (self.name)


class Precondition(Base):
    __tablename__ = 'precondition'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    material_id = Column(Integer, ForeignKey('material.id'))
    count_material = Column(Integer)
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    building_id = Column(Integer, ForeignKey('building.id'))
    possible_action = relationship("PossibleAction", back_populates="precondition")


class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    material_id = Column(Integer, ForeignKey('material.id'))
    count_material = Column(Integer)
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    building_id = Column(Integer, ForeignKey('building.id'))
    possible_action = relationship("PossibleAction", back_populates="result")


Base.metadata.create_all(engine)
