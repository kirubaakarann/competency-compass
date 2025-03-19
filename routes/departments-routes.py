from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Department, JobRole, db
from sqlalchemy.exc import SQLAlchemyError

departments = Blueprint('departments', __name__)

@departments.route('/')
def index():
    departments = Department.query.all()
    return render_template('departments/index.html', departments=departments)

@departments.route('/create')
def create():
    return render_template('departments/create.html')

@departments.route('/store', methods=['POST'])
def store():
    try:
        name = request.form['name']
        description = request.form['description']
        
        department = Department(
            name=name,
            description=description
        )
        
        db.session.add(department)
        db.session.commit()
        
        flash('Department created successfully!', 'success')
        return redirect(url_for('departments.view', id=department.id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error creating department: {str(e)}', 'error')
        return redirect(url_for('departments.create'))

@departments.route('/<int:id>')
def view(id):
    department = Department.query.get_or_404(id)
    job_roles = JobRole.query.filter_by(department_id=id).all()
    
    return render_template('departments/view.html', 
                          department=department, 
                          job_roles=job_roles)

@departments.route('/<int:id>/edit')
def edit(id):
    department = Department.query.get_or_404(id)
    return render_template('departments/edit.html', department=department)

@departments.route('/<int:id>/update', methods=['POST'])
def update(id):
    try:
        department = Department.query.get_or_404(id)
        
        department.name = request.form['name']
        department.description = request.form['description']
        
        db.session.commit()
        
        flash('Department updated successfully!', 'success')
        return redirect(url_for('departments.view', id=id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error updating department: {str(e)}', 'error')
        return redirect(url_for('departments.edit', id=id))

@departments.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    try:
        department = Department.query.get_or_404(id)
        
        # Check if there are job roles in this department
        job_roles_count = JobRole.query.filter_by(department_id=id).count()
        if job_roles_count > 0:
            flash(f'Cannot delete department. There are {job_roles_count} job roles assigned to this department.', 'error')
            return redirect(url_for('departments.view', id=id))
        
        db.session.delete(department)
        db.session.commit()
        
        flash('Department deleted successfully!', 'success')
        return redirect(url_for('departments.index'))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting department: {str(e)}', 'error')
        return redirect(url_for('departments.view', id=id))
