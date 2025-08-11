from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    dob = db.Column(db.Date)
    race = db.Column(db.String(80))
    address = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CaseNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_type = db.Column(db.String(40))
    note = db.Column(db.Text)
    provided_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assessment_type = db.Column(db.String(80))
    score_json = db.Column(db.Text)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True)
    employer_name = db.Column(db.String(160))
    job_title = db.Column(db.String(120))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    wage = db.Column(db.Float)
    status = db.Column(db.String(40))

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True)
    school_name = db.Column(db.String(160))
    program = db.Column(db.String(160))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(40))

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(10))
    status = db.Column(db.String(80))
    note = db.Column(db.Text)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    contact_name = db.Column(db.String(160))
    phone = db.Column(db.String(40))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    contact_name = db.Column(db.String(160))
    phone = db.Column(db.String(40))
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), index=True, nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='referred')
    note = db.Column(db.Text)
    referred_at = db.Column(db.DateTime, default=datetime.utcnow)
