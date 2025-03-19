from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import DevelopmentPlan, Employee, db
from sqlalchemy.exc import SQLAlchemyError

development_plans = Blueprint('development_plans', __name__)

@development_plans.route('/')
def index():
    development_plans = DevelopmentPlan.query.all()
    return render_template('development_plans/index.html', development_plans=development_plans)

@development_plans.route('/create')
def create():
    employee_id = request.args.get('employee_id', None, type=int)
    
    if employee_id:
        employee = Employee.query.get_or_404(employee_id)
        return render_template('development_plans/create.html', employee=employee)
    
    employees = Employee.query.all()
    return render_template('development_plans/select_employee.html', employees=employees)

@development_plans.route('/store', methods=['POST'])
def store():
    try:
        # Add logic to create a development plan
        # This is a placeholder and should be customized based on your specific requirements
        employee_id = request.form['employee_id']
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        development_plan = DevelopmentPlan(
            employee_id=employee_id,
            created_by_id=request.form.get('created_by_id'),  # Assuming you track who created the plan
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(development_plan)
        db.session.commit()
        
        flash('Development plan created successfully!', 'success')
        return redirect(url_for('development_plans.index'))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error creating development plan: {str(e)}', 'error')
        return redirect(url_for('development_plans.create'))
