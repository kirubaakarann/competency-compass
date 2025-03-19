from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Department(db.Model):
    """Department model for storing department information"""
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competencies = db.relationship('Competency', backref='department', lazy=True)
    employees = db.relationship('Employee', backref='department', lazy=True)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Department {self.name}>'
        
    def to_dict(self):
        """Convert department to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Competency(db.Model):
    """Competency model for storing competency information"""
    __tablename__ = 'competencies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    behaviors = db.relationship('CompetencyBehavior', backref='competency', lazy=True, cascade='all, delete-orphan')
    role_competencies = db.relationship('RoleCompetency', backref='competency', lazy=True, cascade='all, delete-orphan')

class CompetencyBehavior(db.Model):
    """CompetencyBehavior model for storing behaviors associated with competencies"""
    __tablename__ = 'competency_behaviors'

    id = db.Column(db.Integer, primary_key=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1=Basic, 2=Intermediate, 3=Advanced, etc.
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JobRole(db.Model):
    """JobRole model for storing job role information"""
    __tablename__ = 'job_roles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role_competencies = db.relationship('RoleCompetency', backref='job_role', lazy=True, cascade='all, delete-orphan')
    employees = db.relationship('Employee', backref='job_role', lazy=True)

class RoleCompetency(db.Model):
    """RoleCompetency model for mapping competencies to job roles"""
    __tablename__ = 'role_competencies'

    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    required_level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Employee(db.Model):
    """Employee model for storing employee information"""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    hire_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='employee', lazy=True)
    development_plans = db.relationship('DevelopmentPlan', backref='employee', lazy=True)

class Assessment(db.Model):
    """Assessment model for storing employee assessments"""
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    assessor_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)  # Self-assessment if NULL
    assessment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('AssessmentRating', backref='assessment', lazy=True, cascade='all, delete-orphan')
    assessor = db.relationship('Employee', foreign_keys=[assessor_id], backref='conducted_assessments')

class AssessmentRating(db.Model):
    """AssessmentRating model for storing individual competency ratings in an assessment"""
    __tablename__ = 'assessment_ratings'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 or whatever scale is used
    evidence = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competency = db.relationship('Competency')

class DevelopmentPlan(db.Model):
    """DevelopmentPlan model for storing employee development plans"""
    __tablename__ = 'development_plans'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    actions = db.relationship('DevelopmentAction', backref='development_plan', lazy=True, cascade='all, delete-orphan')

class DevelopmentAction(db.Model):
    """DevelopmentAction model for storing individual actions in a development plan"""
    __tablename__ = 'development_actions'

    id = db.Column(db.Integer, primary_key=True)
    development_plan_id = db.Column(db.Integer, db.ForeignKey('development_plans.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    action_description = db.Column(db.Text, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='not_started')  # not_started, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competency = db.relationship('Competency')

class AIRecommendation(db.Model):
    """AIRecommendation model for storing AI-generated development recommendations"""
    __tablename__ = 'ai_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    resources = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', backref='ai_recommendations')
    competency = db.relationship('Competency')
