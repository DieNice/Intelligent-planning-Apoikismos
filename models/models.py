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

engine = create_engine('sqlite:///ipa.db', echo=False, connect_args={'check_same_thread': False})
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
    material_precondition = relationship("MaterialPrecondition", back_populates="material_parent")
    material_result = relationship("MaterialResult", back_populates="material_parent")

    __mapper_args__ = {
        'polymorphic_identity': 'material'
    }

    def __repr__(self):
        return "<Material('%s','%s')>" % (self.name, self.description)


class Instrument(SimpleEntity):
    __tablename__ = 'instrument'
    id = Column(Integer, ForeignKey('simple_entity.id'), primary_key=True)
    instrument_precondition = relationship("InstrumentPrecondition", back_populates="instrument_parent")
    instrument_result = relationship("InstrumentResult", back_populates="instrument_parent")

    __mapper_args__ = {
        'polymorphic_identity': 'instrument'
    }

    def __repr__(self):
        return "<Instrument('%s','%s')>" % (self.name, self.description)


class Building(SimpleEntity):
    __tablename__ = 'building'
    id = Column(Integer, ForeignKey('simple_entity.id'), primary_key=True)
    building_precondition = relationship("BuildingPrecondition", back_populates="building_parent")
    building_result = relationship("BuildingResult", back_populates="building_parent")

    __mapper_args__ = {
        'polymorphic_identity': 'building'
    }

    def __repr__(self):
        return "<Building('%s','%s')>" % (self.name, self.description)


class PossibleAction(Base):
    __tablename__ = 'possible_action'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    InstrumentPrecondition = relationship("InstrumentPrecondition")
    MaterialPrecondition = relationship("MaterialPrecondition")
    BuildingPrecondition = relationship("BuildingPrecondition")
    InstrumentResult = relationship("InstrumentResult")
    MaterialResult = relationship("MaterialResult")
    BuildingResult = relationship("BuildingResult")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<PossibleAction('%s')>" % (self.name)

    def __str__(self):
        return "<PossibleAction('%s')>" % (self.name)


class InstrumentPrecondition(Base):
    __tablename__ = 'instrument_precondition'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    possible_action = relationship("PossibleAction", back_populates="InstrumentPrecondition")
    instrument_parent = relationship("Instrument", back_populates="instrument_precondition")

    def __init__(self, action_id, instrument_id):
        self.action_id = action_id
        self.instrument_id = instrument_id

    def __repr__(self):
        return "<InstrumentPrecondition('%s','%s')>" % (
            str(self.action_id), str(self.instrument_id))


class MaterialPrecondition(Base):
    __tablename__ = 'material_precondition'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    material_id = Column(Integer, ForeignKey('material.id'))
    count = Column(Integer)
    possible_action = relationship("PossibleAction", back_populates="MaterialPrecondition")
    material_parent = relationship("Material", back_populates="material_precondition")

    def __init__(self, action_id, materials_id, count):
        self.action_id = action_id
        self.material_id = materials_id
        self.count = count

    def __repr__(self):
        return "<MaterialPrecondition('%s','%s','%s')>" % (
            str(self.material_id), str(self.action_id), str(self.count))


class BuildingPrecondition(Base):
    __tablename__ = 'building_precondition'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    building_id = Column(Integer, ForeignKey('building.id'))
    possible_action = relationship("PossibleAction", back_populates="BuildingPrecondition")
    building_parent = relationship("Building", back_populates="building_precondition")

    def __init__(self, action_id, building_id):
        self.action_id = action_id
        self.building_id = building_id

    def __repr__(self):
        return "<BuildingPrecondition('%s','%s')>" % (
            str(self.action_id), str(self.building_id))


class InstrumentResult(Base):
    __tablename__ = 'instrument_result'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    instrument_id = Column(Integer, ForeignKey('instrument.id'))
    possible_action = relationship("PossibleAction", back_populates="InstrumentResult")
    instrument_parent = relationship("Instrument", back_populates="instrument_result")

    def __init__(self, action_id, instrument_id):
        self.action_id = action_id
        self.instrument_id = instrument_id

    def __repr__(self):
        return "<InstrumentResult('%s','%s')>" % (
            str(self.action_id), str(self.instrument_id))


class MaterialResult(Base):
    __tablename__ = 'material_result'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    material_id = Column(Integer, ForeignKey('material.id'))
    count = Column(Integer)
    possible_action = relationship("PossibleAction", back_populates="MaterialResult")
    material_parent = relationship("Material", back_populates="material_result")

    def __init__(self, action_id, materials_id, count):
        self.action_id = action_id
        self.material_id = materials_id
        self.count = count

    def __repr__(self):
        return "<MaterialResult('%s','%s','%s')>" % (
            str(self.material_id), str(self.action_id), str(self.count))


class BuildingResult(Base):
    __tablename__ = 'building_result'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('possible_action.id'))
    building_id = Column(Integer, ForeignKey('building.id'))
    possible_action = relationship("PossibleAction", back_populates="BuildingResult")
    building_parent = relationship("Building", back_populates="building_result")

    def __init__(self, action_id, building_id):
        self.action_id = action_id
        self.building_id = building_id

    def __repr__(self):
        return "<BuildingResult('%s','%s')>" % (
            str(self.action_id), str(self.building_id))


Base.metadata.create_all(engine)
