from datetime import datetime
from .extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(64))

class Participant(db.Model):
    __tablename__ = "participants"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name  = db.Column(db.String(120))
    dob        = db.Column(db.Date)
    race       = db.Column(db.String(64))
    address    = db.Column(db.String(255))
    email      = db.Column(db.String(255))
    phone      = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CaseNote(db.Model):
    __tablename__ = "case_notes"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False, index=True)
    content = db.Column(db.Text)
    staff_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False, index=True)
    service_type = db.Column(db.String(120))
    note = db.Column(db.Text)
    staff_id = db.Column(db.Integer)
    provided_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Employer(db.Model):
    __tablename__ = "employers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255))
    phone = db.Column(db.String(64))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))

class Provider(db.Model):
    __tablename__ = "providers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255))
    phone = db.Column(db.String(64))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))

class Referral(db.Model):
    __tablename__ = "referrals"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=False, index=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("employers.id"), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"), nullable=True)
    staff_id = db.Column(db.Integer)
    status = db.Column(db.String(64), default="referred")
    note = db.Column(db.Text)
    referred_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Assessment(db.Model):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), index=True, nullable=False)
    kind = db.Column(db.String(64))
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Employment(db.Model):
    __tablename__ = "employment"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), index=True, nullable=False)
    employer = db.Column(db.String(255))
    position = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

class Education(db.Model):
    __tablename__ = "education"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), index=True, nullable=False)
    school = db.Column(db.String(255))
    program = db.Column(db.String(255))
    status = db.Column(db.String(64))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

class Milestone(db.Model):
    __tablename__ = "milestones"
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participants.id"), index=True, nullable=False)
    name = db.Column(db.String(255))
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
