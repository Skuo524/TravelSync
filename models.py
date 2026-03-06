from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Trip(Base):
    __tablename__ = 'trips'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    invite_code = Column(String(50), unique=True, nullable=False)
    
    # Relationship to schedule items
    items = relationship("ScheduleItem", back_populates="trip", cascade="all, delete-orphan")

class ScheduleItem(Base):
    __tablename__ = 'schedule_items'
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    day_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    start_time = Column(Time, nullable=True) # Allow null for items without fixed time
    duration = Column(Integer, default=60) # Duration in minutes
    location = Column(Text, nullable=True)
    note = Column(Text, nullable=True)
    is_proposal = Column(Boolean, default=False)
    
    trip = relationship("Trip", back_populates="items")
    votes = relationship("Vote", back_populates="item", cascade="all, delete-orphan")

class Vote(Base):
    __tablename__ = 'votes'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('schedule_items.id'), nullable=False)
    user_name = Column(String(100), nullable=False)
    
    item = relationship("ScheduleItem", back_populates="votes")
