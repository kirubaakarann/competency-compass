from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Employee, JobRole, Competency, RoleCompetency, Assessment, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime

employees = Blueprint('employees', __name__)

@employees.route('/')
def index():
    employees = Employee.query.all()
    return render_template('employees/index.html', employees=employees)

@employees.route('/create')
def create():
    job_roles = JobRole.query.all()
    job_role_id = request.args.get('job_role_id', None, type=int)
    
    return render_template('employees/create.html', 
                           job_roles=job_roles,
                           selected_job_role_id=job_role_id)

@employees.route('/store', methods=['POST'])
def store():
    try:
        name = request.form['name']
        email = request.form['email']
        job_role_id = request.form['job_role_id']
        hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form['hire_date'] else None
        
        # Create new employee
        employee = Employee(
            name=name,
            email=email,
            job_role_id=job_role_id,
            hire_date=hire_date
        )
        
        db.session.add(employee)
        db.session.commit()
        
        flash('Employee created successfully!', 'success')
        return redirect(url_for('employees.view', id=employee.id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error creating employee: {str(e)}', 'error')
        return redirect(url_for('employees.create'))

@employees.route('/<int:id>')
def view(id):
    employee = Employee.query.get_or_404(id)
    job_role = employee.job_role
    
    # Get competency requirements for the job role
    role_competencies = RoleCompetency.query.filter_by(job_role_id=job_role.id).all()
    
    # Get most recent assessment if exists
    latest_assessment = Assessment.query.filter_by(employee_id=id).order_by(Assessment.assessment_date.desc()).first()
    
    # Initialize competency data structure
    competency_data = []
    for rc in role_competencies:
        competency_info = {
            'id': rc.competency_id,
            'name': rc.competency.name,
            'required_level': rc.required_level,
            'weight': rc.weight,
            'current_level': 0  # Default if no assessment
        }
        
        # Add current level if assessment exists
        if latest_assessment:
            for rating in latest_assessment.ratings:
                if rating.competency_id == rc.competency_id:
                    competency_info['current_level'] = rating.rating
                    competency_info['evidence'] = rating.evidence
                    break
        
        competency_data.append(competency_info)
    
    # Get all assessments for this employee
    assessments = Assessment.query.filter_by(employee_id=id).order_by(Assessment.assessment_date.desc()).all()
    
    return render_template('employees/view.html', 
                           employee=employee, 
                           job_role=job_role,
                           competency_data=competency_data,
                           latest_assessment=latest_assessment,
                           assessments=assessments)

@employees.route('/<int:id>/edit')
def edit(id):
    employee = Employee.query.get_or_404(id)
    job_roles = JobRole.query.all()
    
    return render_template('employees/edit.html', 
                           employee=employee, 
                           job_roles=job_roles)

@employees.route('/<int:id>/update', methods=['POST'])
def update(id):
    try:
        employee = Employee.query.get_or_404(id)
        
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.job_role_id = request.form['job_role_id']
        employee.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form['hire_date'] else None
        
        db.session.commit()
        
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees.view', id=id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error updating employee: {str(e)}', 'error')
        return redirect(url_for('employees.edit', id=id))

@employees.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    try:
        employee = Employee.query.get_or_404(id)
        
        # Check if employee has assessments
        assessment_count = Assessment.query.filter_by(employee_id=id).count()
        if assessment_count > 0:
            flash(f'Cannot delete employee. There are {assessment_count} assessments associated with this employee.', 'error')
            return redirect(url_for('employees.view', id=id))
        
        # Delete employee
        db.session.delete(employee)
        db.session.commit()
        
        flash('Employee deleted successfully!', 'success')
        return redirect(url_for('employees.index'))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'error')
        return redirect(url_for('employees.view', id=id))

@employees.route('/<int:id>/competency-radar')
def competency_radar(id):
    employee = Employee.query.get_or_404(id)
    job_role = employee.job_role
    
    # Get competency requirements for the job role
    role_competencies = RoleCompetency.query.filter_by(job_role_id=job_role.id).all()
    
    # Get most recent assessment if exists
    latest_assessment = Assessment.query.filter_by(employee_id=id).order_by(Assessment.assessment_date.desc()).first()
    
    # Build data for radar chart
    labels = []
    required_data = []
    current_data = []
    
    for rc in role_competencies:
        labels.append(rc.competency.name)
        required_data.append(rc.required_level)
        
        # Get current level if assessment exists
        current_level = 0
        if latest_assessment:
            for rating in latest_assessment.ratings:
                if rating.competency_id == rc.competency_id:
                    current_level = rating.rating
                    break
        
        current_data.append(current_level)
    
    return render_template('employees/competency_radar.html',
                          employee=employee,
                          job_role=job_role,
                          labels=labels,
                          required_data=required_data,
                          current_data=current_data)
