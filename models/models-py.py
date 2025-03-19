from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class JobRole(db.Model):
    __tablename__ = 'job_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    taxonomy_used = db.Column(db.String(50), default='Simplified SFIA')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    competencies = db.relationship('JobRoleCompetency', back_populates='job_role', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<JobRole {self.title}>"


class Competency(db.Model):
    __tablename__ = 'competencies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationships
    taxonomy_competencies = db.relationship('TaxonomyCompetency', back_populates='competency')
    job_role_competencies = db.relationship('JobRoleCompetency', back_populates='competency')
    employee_competencies = db.relationship('EmployeeCompetency', back_populates='competency')
    training_resources = db.relationship('TrainingResource', back_populates='competency')
    
    def __repr__(self):
        return f"<Competency {self.name}>"


class TaxonomyCompetency(db.Model):
    __tablename__ = 'taxonomy_competencies'
    
    id = db.Column(db.Integer, primary_key=True)
    taxonomy_name = db.Column(db.String(50), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    recommended_level = db.Column(db.Integer, nullable=False)
    
    # Relationships
    competency = db.relationship('Competency', back_populates='taxonomy_competencies')
    
    __table_args__ = (db.UniqueConstraint('taxonomy_name', 'competency_id'),)
    
    def __repr__(self):
        return f"<TaxonomyCompetency {self.taxonomy_name}:{self.competency.name}>"


class JobRoleCompetency(db.Model):
    __tablename__ = 'job_role_competencies'
    
    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    required_level = db.Column(db.Integer, nullable=False)
    
    # Relationships
    job_role = db.relationship('JobRole', back_populates='competencies')
    competency = db.relationship('Competency', back_populates='job_role_competencies')
    
    __table_args__ = (db.UniqueConstraint('job_role_id', 'competency_id'),)
    
    def __repr__(self):
        return f"<JobRoleCompetency {self.job_role.title}:{self.competency.name}>"


class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    competencies = db.relationship('EmployeeCompetency', back_populates='employee', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Employee {self.name}>"


class EmployeeCompetency(db.Model):
    __tablename__ = 'employee_competencies'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'), nullable=False)
    current_level = db.Column(db.Integer, nullable=False)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='competencies')
    competency = db.relationship('Competency', back_populates='employee_competencies')
    
    __table_args__ = (db.UniqueConstraint('employee_id', 'competency_id'),)
    
    def __repr__(self):
        return f"<EmployeeCompetency {self.employee.name}:{self.competency.name}>"


class TrainingResource(db.Model):
    __tablename__ = 'training_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    resource_type = db.Column(db.String(50))  # Online Course, Workshop, etc.
    url = db.Column(db.String(200))
    competency_id = db.Column(db.Integer, db.ForeignKey('competencies.id'))
    
    # Relationships
    competency = db.relationship('Competency', back_populates='training_resources')
    
    def __repr__(self):
        return f"<TrainingResource {self.name}>"
