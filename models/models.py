from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import with_polymorphic
from sqlalchemy import inspect
from sqlalchemy import func, and_, or_, not_, alias
from sqlalchemy.orm import aliased
from sqlalchemy import asc
from sqlalchemy import outerjoin

engine = create_engine('sqlite:///ipa.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class SimpleEntity(Base):
    __tablename__ = 'simple_entity'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def getstr(self):
        return (self.name, self.description)

    __mapper_args__ = {
        'polymorphic_identity': 'simple_entity',
        'polymorphic_on': type,
    }


class Material(SimpleEntity):
    __tablename__ = 'material'
    id = Column(Integer, ForeignKey('simple_entity.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'material'
    }

    def __repr__(self):
        return "<Material('%s','%s')>" % (self.name, self.description)


class Instrument(SimpleEntity):
    __tablename__ = 'instrument'
    id = Column(Integer, ForeignKey('simple_entity.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'instrument'
    }

    def __repr__(self):
        return "<Instrument('%s','%s')>" % (self.name, self.description)


class Building(SimpleEntity):
    __tablename__ = 'building'
    id = Column(Integer, ForeignKey('simple_entity.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'building'
    }

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
        return "<PossibleAction('%s')>" % (self.name)


class Precondition(Base):
    __tablename__ = 'precondition'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    material_id = Column(Integer, ForeignKey('material.id'))
    count_material = Column(Integer)
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    building_id = Column(Integer, ForeignKey('building.id'))
    possible_action = relationship("PossibleAction", back_populates="precondition")

    def __repr__(self):
        return "<Precondition('%s','%s','%s','%s')>" % (
            str(self.material_id), str(self.count_material), str(self.instrument_id), str(self.building_id))


class Result(Base):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    material_id = Column(Integer, ForeignKey('material.id'))
    count_material = Column(Integer)
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    building_id = Column(Integer, ForeignKey('building.id'))
    possible_action = relationship("PossibleAction", back_populates="result")

    def __repr__(self):
        return "<Result('%s','%s','%s','%s')>" % (
            str(self.material_id), str(self.count_material), str(self.instrument_id), str(self.building_id))


Base.metadata.create_all(engine)
