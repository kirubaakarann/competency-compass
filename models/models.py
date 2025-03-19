from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    job_roles = db.relationship('JobRole', backref='department', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Competency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    behaviors = db.relationship('CompetencyBehavior', backref='competency', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CompetencyBehavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1-5
    description = db.Column(db.Text, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JobRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    
    competencies = db.relationship('RoleCompetency', backref='job_role', lazy=True)
    employees = db.relationship('Employee', backref='job_role', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RoleCompetency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_role.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    required_level = db.Column(db.Integer, nullable=False)  # 1-5
    weight = db.Column(db.Integer, nullable=False, default=5)  # 1-10
    
    competency = db.relationship('Competency')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Association table for employee competency ratings
employee_competency_ratings = db.Table('employee_competency_ratings',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), primary_key=True),
    db.Column('competency_id', db.Integer, db.ForeignKey('competency.id'), primary_key=True),
    db.Column('rating', db.Integer, nullable=False),  # 1-5
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_role.id'), nullable=False)
    hire_date = db.Column(db.Date)
    
    # Many-to-many relationship with Competency through employee_competency_ratings
    competency_ratings = db.relationship('Competency', secondary=employee_competency_ratings,
                                        lazy='subquery', backref=db.backref('employees', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    assessor_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    employee = db.relationship('Employee', foreign_keys=[employee_id])
    assessor = db.relationship('Employee', foreign_keys=[assessor_id])
    ratings = db.relationship('AssessmentRating', backref='assessment', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AssessmentRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    evidence = db.Column(db.Text)
    
    competency = db.relationship('Competency')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DevelopmentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Draft')  # Draft, Active, Completed, Canceled
    
    employee = db.relationship('Employee', foreign_keys=[employee_id])
    created_by = db.relationship('Employee', foreign_keys=[created_by_id])
    actions = db.relationship('DevelopmentAction', backref='plan', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DevelopmentAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('development_plan.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Not Started')  # Not Started, In Progress, Completed
    
    competency = db.relationship('Competency')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competency.id'), nullable=False)
    recommendation_type = db.Column(db.String(50))  # Training, Resource, Practice, etc.
    content = db.Column(db.Text, nullable=False)
    is_applied = db.Column(db.Boolean, default=False)
    
    employee = db.relationship('Employee')
    competency = db.relationship('Competency')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
