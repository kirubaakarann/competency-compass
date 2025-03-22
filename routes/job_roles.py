from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import JobRole, Competency, RoleCompetency, db
from sqlalchemy.exc import SQLAlchemyError

job_roles = Blueprint('job_roles', __name__)

@job_roles.route('/')
def index():
    job_roles = JobRole.query.all()
    return render_template('job_roles/index.html', job_roles=job_roles)

@job_roles.route('/create')
def create():
    competencies = Competency.query.all()
    return render_template('job_roles/create.html', competencies=competencies)

@job_roles.route('/store', methods=['POST'])
def store():
    try:
        title = request.form['title']
        description = request.form.get('description', '')
        
        # Create new job role
        job_role = JobRole(
            title=title,
            description=description
        )
        
        db.session.add(job_role)
        db.session.flush()  # Get the ID of the new job role
        
        # Process selected competencies
        competency_ids = request.form.getlist('competency_ids[]')
        
        if competency_ids:
            for comp_id in competency_ids:
                # Get the required level for this competency
                required_level = request.form.get(f'required_levels[{comp_id}]', 3)
                
                # Create role competency mapping
                role_competency = RoleCompetency(
                    job_role_id=job_role.id,
                    competency_id=int(comp_id),
                    required_level=int(required_level)
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
    return render_template('job_roles/view.html', job_role=job_role)

@job_roles.route('/<int:id>/edit')
def edit(id):
    job_role = JobRole.query.get_or_404(id)
    competencies = Competency.query.all()
    
    # Create a dictionary of existing role competencies for easier access in template
    role_competencies_dict = {}
    for rc in job_role.role_competencies:
        role_competencies_dict[rc.competency_id] = rc
    
    return render_template('job_roles/edit.html', 
                          job_role=job_role, 
                          competencies=competencies,
                          role_competencies_dict=role_competencies_dict)

@job_roles.route('/<int:id>/update', methods=['POST'])
def update(id):
    try:
        job_role = JobRole.query.get_or_404(id)
        
        job_role.title = request.form['title']
        job_role.description = request.form.get('description', '')
        
        # Remove existing role competencies
        RoleCompetency.query.filter_by(job_role_id=id).delete()
        
        # Process selected competencies
        competency_ids = request.form.getlist('competency_ids[]')
        
        if competency_ids:
            for comp_id in competency_ids:
                # Get the required level for this competency
                required_level = request.form.get(f'required_levels[{comp_id}]', 3)
                
                # Create new role competency mapping
                role_competency = RoleCompetency(
                    job_role_id=job_role.id,
                    competency_id=int(comp_id),
                    required_level=int(required_level)
                )
                
                db.session.add(role_competency)
        
        db.session.commit()
        flash('Job role updated successfully!', 'success')
        return redirect(url_for('job_roles.view', id=id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error updating job role: {str(e)}', 'error')
        return redirect(url_for('job_roles.edit', id=id))

@job_roles.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    try:
        job_role = JobRole.query.get_or_404(id)
        
        # Check if this job role is assigned to any employees
        if job_role.employees:
            flash('Cannot delete job role. It is assigned to one or more employees.', 'error')
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
