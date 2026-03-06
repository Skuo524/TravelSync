import uuid
from sqlalchemy.orm import Session
from models import Trip, ScheduleItem, Vote
from database import SessionLocal
from datetime import datetime, time

def generate_invite_code():
    """Generate a unique short invite code."""
    return str(uuid.uuid4())[:8].upper()

def create_trip(db: Session, title: str, start_date: datetime.date, end_date: datetime.date):
    """Create a new trip and return it."""
    invite_code = generate_invite_code()
    new_trip = Trip(
        title=title,
        start_date=start_date,
        end_date=end_date,
        invite_code=invite_code
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip

def get_trip_by_invite_code(db: Session, invite_code: str):
    """Find a trip using its invite code."""
    return db.query(Trip).filter(Trip.invite_code == invite_code).first()

def get_trip_by_id(db: Session, trip_id: int):
    """Find a trip by ID."""
    return db.query(Trip).filter(Trip.id == trip_id).first()

def add_activity(db: Session, trip_id: int, day_number: int, title: str, 
                 start_time: time = None, duration: int = 60, 
                 location: str = "", note: str = "", is_proposal: bool = False):
    """Add a new activity or proposal to a trip."""
    item = ScheduleItem(
        trip_id=trip_id,
        day_number=day_number,
        title=title,
        start_time=start_time,
        duration=duration,
        location=location,
        note=note,
        is_proposal=is_proposal
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_schedule_items(db: Session, trip_id: int, day_number: int = None):
    """Get all schedule items for a trip, optionally filtered by day."""
    query = db.query(ScheduleItem).filter(ScheduleItem.trip_id == trip_id)
    if day_number is not None:
        query = query.filter(ScheduleItem.day_number == day_number)
    # Sort by start_time (nulls last)
    return query.order_by(ScheduleItem.start_time.asc()).all()

def vote_for_item(db: Session, item_id: int, user_name: str):
    """Record a vote for a proposal item."""
    # Check if already voted for this item
    existing_vote = db.query(Vote).filter(
        Vote.item_id == item_id, 
        Vote.user_name == user_name
    ).first()
    
    if not existing_vote:
        new_vote = Vote(item_id=item_id, user_name=user_name)
        db.add(new_vote)
        db.commit()
        return True
    return False

def finalize_proposal(db: Session, item_id: int):
    """Convert a proposal to a fixed activity and remove competing proposals in the same slot (simplified)."""
    item = db.query(ScheduleItem).filter(ScheduleItem.id == item_id).first()
    if item:
        item.is_proposal = False
        db.commit()
        db.refresh(item)
        return item
    return None

def delete_schedule_item(db: Session, item_id: int):
    """Remove an item from the schedule."""
    item = db.query(ScheduleItem).filter(ScheduleItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
