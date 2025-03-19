from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import JobRole, Department, Competency, RoleCompetency, Employee, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

job_roles = Blueprint('job_roles', __name__)

@job_roles.route('/')
def index():
    job_roles = JobRole.query.all()
    return render_template('job_roles/index.html', job_roles=job_roles)

@job_roles.route('/create')
def create():
    departments = Department.query.all()
    competencies = Competency.query.all()
    return render_template('job_roles/create.html', departments=departments, competencies=competencies)

@job_roles.route('/store', methods=['POST'])
def store():
    try:
        title = request.form['title']
        description = request.form['description']
        department_id = request.form['department_id']
        
        # Create new job role
        job_role = JobRole(
            title=title,
            description=description,
            department_id=department_id
        )
        
        db.session.add(job_role)
        db.session.flush()  # Get the ID of the new job role
        
        # Add competencies
        competency_ids = request.form.getlist('competency_ids[]')
        levels = request.form.getlist('levels[]')
        weights = request.form.getlist('weights[]')
        
        for i in range(len(competency_ids)):
            role_competency = RoleCompetency(
                job_role_id=job_role.id,
                competency_id=competency_ids[i],
                required_level=levels[i],
                weight=weights[i]
            )
            db.session.add(role_competency)
        
        db.session.commit()
        flash('Job role created successfully!', 'success')
        return redirect(url_for('job_roles.view', id=job_role.id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error creating job role: {str(e)}', 'error')
        return redirect(url_for('job_roles.create'))

@job_roles.route('/<int:id>')
def view(id):
    job_role = JobRole.query.get_or_404(id)
    role_competencies = RoleCompetency.query.filter_by(job_role_id=id).all()
    
    # Get employees in this role with their average competency level
    employees = db.session.query(
        Employee,
        func.avg(db.case(
            (db.and_(
                RoleCompetency.competency_id == Employee.competency_ratings.c.competency_id,
                RoleCompetency.job_role_id == id
            ), Employee.competency_ratings.c.rating),
            else_=0
        )).label('avg_competency')
    ).filter(
        Employee.job_role_id == id
    ).group_by(
        Employee.id
    ).all()
    
    # Create a list of employee objects with avg_competency attribute
    employees_with_avg = []
    for emp, avg in employees:
        emp.avg_competency = avg or 0
        employees_with_avg.append(emp)
    
    return render_template('job_roles/view.html', 
                           job_role=job_role, 
                           role_competencies=role_competencies, 
                           employees=employees_with_avg)

@job_roles.route('/<int:id>/edit')
def edit(id):
    job_role = JobRole.query.get_or_404(id)
    departments = Department.query.all()
    competencies = Competency.query.all()
    role_competencies = RoleCompetency.query.filter_by(job_role_id=id).all()
    
    return render_template('job_roles/edit.html', 
                           job_role=job_role, 
                           departments=departments, 
                           competencies=competencies, 
                           role_competencies=role_competencies)

@job_roles.route('/<int:id>/update', methods=['POST'])
def update(id):
    try:
        job_role = JobRole.query.get_or_404(id)
        
        job_role.title = request.form['title']
        job_role.description = request.form['description']
        job_role.department_id = request.form['department_id']
        
        # Delete existing role competencies
        RoleCompetency.query.filter_by(job_role_id=id).delete()
        
        # Add updated competencies
        competency_ids = request.form.getlist('competency_ids[]')
        levels = request.form.getlist('levels[]')
        weights = request.form.getlist('weights[]')
        
        for i in range(len(competency_ids)):
            role_competency = RoleCompetency(
                job_role_id=job_role.id,
                competency_id=competency_ids[i],
                required_level=levels[i],
                weight=weights[i]
            )
            db.session.add(role_competency)
        
        db.session.commit()
        flash('Job role updated successfully!', 'success')
        return redirect(url_for('job_roles.view', id=job_role.id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error updating job role: {str(e)}', 'error')
        return redirect(url_for('job_roles.edit', id=id))

@job_roles.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    try:
        job_role = JobRole.query.get_or_404(id)
        
        # Check if there are employees in this role
        employees = Employee.query.filter_by(job_role_id=id).count()
        if employees > 0:
            flash(f'Cannot delete job role. There are {employees} employees assigned to this role.', 'error')
            return redirect(url_for('job_roles.view', id=id))
        
        # Delete role competencies first
        RoleCompetency.query.filter_by(job_role_id=id).delete()
        
        # Delete job role
        db.session.delete(job_role)
        db.session.commit()
        
        flash('Job role deleted successfully!', 'success')
        return redirect(url_for('job_roles.index'))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting job role: {str(e)}', 'error')
        return redirect(url_for('job_roles.view', id=id))
