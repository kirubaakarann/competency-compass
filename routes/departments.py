from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Department

departments = Blueprint('departments', __name__, url_prefix='/departments')

@departments.route('/')
def index():
    """Display all departments."""
    departments = Department.query.all()
    return render_template('departments/index.html', departments=departments)

@departments.route('/create', methods=['GET'])
def create():
    """Show form to create a new department."""
    return render_template('departments/create.html')

@departments.route('/', methods=['POST'])
def store():
    """Store a new department."""
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Department name is required', 'danger')
        return redirect(url_for('departments.create'))
    
    department = Department(name=name, description=description)
    
    try:
        db.session.add(department)
        db.session.commit()
        flash('Department created successfully', 'success')
        return redirect(url_for('departments.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating department: {str(e)}', 'danger')
        return redirect(url_for('departments.create'))

@departments.route('/<int:id>', methods=['GET'])
def show(id):
    """Show a specific department."""
    department = Department.query.get_or_404(id)
    return render_template('departments/show.html', department=department)

@departments.route('/<int:id>/edit', methods=['GET'])
def edit(id):
    """Show form to edit a department."""
    department = Department.query.get_or_404(id)
    return render_template('departments/edit.html', department=department)

@departments.route('/<int:id>', methods=['POST'])
def update(id):
    """Update a specific department."""
    department = Department.query.get_or_404(id)
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Department name is required', 'danger')
        return redirect(url_for('departments.edit', id=id))
    
    try:
        department.name = name
        department.description = description
        db.session.commit()
        flash('Department updated successfully', 'success')
        return redirect(url_for('departments.show', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating department: {str(e)}', 'danger')
        return redirect(url_for('departments.edit', id=id))

@departments.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a specific department."""
    department = Department.query.get_or_404(id)
    
    try:
        db.session.delete(department)
        db.session.commit()
        flash('Department deleted successfully', 'success')
        return redirect(url_for('departments.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting department: {str(e)}', 'danger')
        return redirect(url_for('departments.show', id=id))
