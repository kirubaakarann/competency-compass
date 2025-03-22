from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Assessment, AssessmentRating, Employee, JobRole, RoleCompetency, Competency, db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

assessments = Blueprint('assessments', __name__)

@assessments.route('/')
def index():
    assessments = Assessment.query.order_by(Assessment.assessment_date.desc()).all()
    return render_template('assessments/index.html', assessments=assessments)

@assessments.route('/create')
def create():
    employee_id = request.args.get('employee_id', None, type=int)
    
    # If no employee specified, show employee selection form
    if not employee_id:
        employees = Employee.query.all()
        return render_template('assessments/select_employee.html', employees=employees)
    
    # Get the employee and their job role
    employee = Employee.query.get_or_404(employee_id)
    job_role = employee.job_role
    
    # Get required competencies for this job role
    role_competencies = RoleCompetency.query.filter_by(job_role_id=job_role.id).all()
    
    # Get potential assessors (all employees)
    assessors = Employee.query.all()
    
    # Get current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('assessments/create.html', 
                          employee=employee,
                          job_role=job_role,
                          role_competencies=role_competencies,
                          assessors=assessors,
                          current_date=current_date)

@assessments.route('/store', methods=['POST'])
def store():
    try:
        employee_id = request.form['employee_id']
        assessor_id = request.form['assessor_id']
        assessment_date = datetime.strptime(request.form['assessment_date'], '%Y-%m-%d').date()
        notes = request.form.get('notes', '')
        
        # Create new assessment
        assessment = Assessment(
            employee_id=employee_id,
            assessor_id=assessor_id,
            assessment_date=assessment_date,
            notes=notes
        )
        
        db.session.add(assessment)
        db.session.flush()  # Get the ID of the new assessment
        
        # Add ratings for each competency
        competency_ids = request.form.getlist('competency_id[]')
        ratings = request.form.getlist('rating[]')
        evidences = request.form.getlist('evidence[]')
        
        for i in range(len(competency_ids)):
            rating = AssessmentRating(
                assessment_id=assessment.id,
                competency_id=competency_ids[i],
                rating=ratings[i],
                evidence=evidences[i]
            )
            db.session.add(rating)
        
        db.session.commit()
        
        flash('Assessment created successfully!', 'success')
        return redirect(url_for('assessments.view', id=assessment.id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error creating assessment: {str(e)}', 'error')
        return redirect(url_for('assessments.create', employee_id=request.form['employee_id']))

@assessments.route('/<int:id>')
def view(id):
    assessment = Assessment.query.get_or_404(id)
    employee = assessment.employee
    job_role = employee.job_role
    
    # Get competency requirements for the job role
    role_competencies = RoleCompetency.query.filter_by(job_role_id=job_role.id).all()
    role_competency_map = {rc.competency_id: rc for rc in role_competencies}
    
    # Build data for each competency rating
    competency_ratings = []
    for rating in assessment.ratings:
        competency_info = {
            'id': rating.competency_id,
            'name': rating.competency.name,
            'rating': rating.rating,
            'evidence': rating.evidence,
            'required_level': role_competency_map.get(rating.competency_id, {}).required_level if rating.competency_id in role_competency_map else 0,
            'weight': role_competency_map.get(rating.competency_id, {}).weight if rating.competency_id in role_competency_map else 0
        }
        competency_ratings.append(competency_info)
    
    # Sort by gap (required - rating) and then by weight
    competency_ratings.sort(key=lambda x: (x['required_level'] - x['rating'], x['weight']), reverse=True)
    
    return render_template('assessments/view.html', 
                          assessment=assessment,
                          employee=employee,
                          job_role=job_role,
                          competency_ratings=competency_ratings)

@assessments.route('/<int:id>/edit')
def edit(id):
    assessment = Assessment.query.get_or_404(id)
    employee = assessment.employee
    job_role = employee.job_role
    
    # Get required competencies for this job role
    role_competencies = RoleCompetency.query.filter_by(job_role_id=job_role.id).all()
    
    # Get potential assessors
    assessors = Employee.query.all()
    
    # Create a map of existing ratings
    ratings_map = {rating.competency_id: rating for rating in assessment.ratings}
    
    return render_template('assessments/edit.html', 
                          assessment=assessment,
                          employee=employee,
                          job_role=job_role,
                          role_competencies=role_competencies,
                          assessors=assessors,
                          ratings_map=ratings_map)

@assessments.route('/<int:id>/update', methods=['POST'])
def update(id):
    try:
        assessment = Assessment.query.get_or_404(id)
        
        assessment.assessor_id = request.form['assessor_id']
        assessment.assessment_date = datetime.strptime(request.form['assessment_date'], '%Y-%m-%d').date()
        assessment.notes = request.form.get('notes', '')
        
        # Delete existing ratings
        AssessmentRating.query.filter_by(assessment_id=id).delete()
        
        # Add updated ratings
        competency_ids = request.form.getlist('competency_id[]')
        ratings = request.form.getlist('rating[]')
        evidences = request.form.getlist('evidence[]')
        
        for i in range(len(competency_ids)):
            rating = AssessmentRating(
                assessment_id=id,
                competency_id=competency_ids[i],
                rating=ratings[i],
                evidence=evidences[i]
            )
            db.session.add(rating)
        
        db.session.commit()
        
        flash('Assessment updated successfully!', 'success')
        return redirect(url_for('assessments.view', id=id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error updating assessment: {str(e)}', 'error')
        return redirect(url_for('assessments.edit', id=id))

@assessments.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    try:
        assessment = Assessment.query.get_or_404(id)
        employee_id = assessment.employee_id
        
        # Delete ratings first
        AssessmentRating.query.filter_by(assessment_id=id).delete()
        
        # Delete assessment
        db.session.delete(assessment)
        db.session.commit()
        
        flash('Assessment deleted successfully!', 'success')
        return redirect(url_for('employees.view', id=employee_id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting assessment: {str(e)}', 'error')
        return redirect(url_for('assessments.view', id=id))
