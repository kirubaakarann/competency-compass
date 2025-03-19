from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Department, JobRole, Employee
from datetime import datetime

employees = Blueprint('employees', __name__, url_prefix='/employees')

@employees.route('/')
def index():
    """Display all employees."""
    employees = Employee.query.all()
    return render_template('employees/index.html', employees=employees)

@employees.route('/create', methods=['GET'])
def create():
    """Show form to create a new employee."""
    # Get all departments and job roles to populate the dropdown menus
    departments = Department.query.all()
    job_roles = JobRole.query.all()
    
    return render_template('employees/create.html', 
                           departments=departments, 
                           job_roles=job_roles)

@employees.route('/', methods=['POST'])
def store():
    """Store a new employee."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    department_id = request.form.get('department_id')
    job_role_id = request.form.get('job_role_id')
    hire_date_str = request.form.get('hire_date')
    
    # Form validation
    if not all([first_name, last_name, email, department_id, job_role_id]):
        flash('All fields except hire date are required', 'danger')
        return redirect(url_for('employees.create'))
    
    # Convert hire_date to datetime object if provided
    hire_date = None
    if hire_date_str:
        try:
            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            return redirect(url_for('employees.create'))
    
    # Check if email is already in use
    if Employee.query.filter_by(email=email).first():
        flash('Email address is already in use', 'danger')
        return redirect(url_for('employees.create'))
    
    # Create a new employee
    employee = Employee(
        first_name=first_name,
        last_name=last_name,
        email=email,
        department_id=department_id,
        job_role_id=job_role_id,
        hire_date=hire_date
    )
    
    try:
        db.session.add(employee)
        db.session.commit()
        flash('Employee created successfully', 'success')
        return redirect(url_for('employees.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating employee: {str(e)}', 'danger')
        return redirect(url_for('employees.create'))

@employees.route('/<int:id>', methods=['GET'])
def show(id):
    """Show a specific employee."""
    employee = Employee.query.get_or_404(id)
    return render_template('employees/show.html', employee=employee)

@employees.route('/<int:id>/edit', methods=['GET'])
def edit(id):
    """Show form to edit an employee."""
    employee = Employee.query.get_or_404(id)
    departments = Department.query.all()
    job_roles = JobRole.query.all()
    
    return render_template('employees/edit.html', 
                           employee=employee,
                           departments=departments,
                           job_roles=job_roles)

@employees.route('/<int:id>', methods=['POST'])
def update(id):
    """Update a specific employee."""
    employee = Employee.query.get_or_404(id)
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    department_id = request.form.get('department_id')
    job_role_id = request.form.get('job_role_id')
    hire_date_str = request.form.get('hire_date')
    
    # Form validation
    if not all([first_name, last_name, email, department_id, job_role_id]):
        flash('All fields except hire date are required', 'danger')
        return redirect(url_for('employees.edit', id=id))
    
    # Check if email is already in use by another employee
    existing_employee = Employee.query.filter_by(email=email).first()
    if existing_employee and existing_employee.id != id:
        flash('Email address is already in use by another employee', 'danger')
        return redirect(url_for('employees.edit', id=id))
    
    # Convert hire_date to datetime object if provided
    hire_date = None
    if hire_date_str:
        try:
            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            return redirect(url_for('employees.edit', id=id))
    
    try:
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.department_id = department_id
        employee.job_role_id = job_role_id
        employee.hire_date = hire_date
        
        db.session.commit()
        flash('Employee updated successfully', 'success')
        return redirect(url_for('employees.show', id=id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating employee: {str(e)}', 'danger')
        return redirect(url_for('employees.edit', id=id))

@employees.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a specific employee."""
    employee = Employee.query.get_or_404(id)
    
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully', 'success')
        return redirect(url_for('employees.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')
        return redirect(url_for('employees.show', id=id))
