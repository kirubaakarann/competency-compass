from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Competency, CompetencyBehavior, db
from sqlalchemy.exc import SQLAlchemyError

competencies = Blueprint('competencies', __name__)

@competencies.route('/')
def index():
    competencies = Competency.query.all()
    return render_template('competencies/index.html', competencies=competencies)

@competencies.route('/create')
def create():
    categories = ['Technical', 'Leadership', 'Interpersonal', 'Business', 'Other']
    return render_template('competencies/create.html', categories=categories)

@competencies.route('/store', methods=['POST'])
def store():
    try:
        name = request.form['name']
        description = request.form['description']
               
        # Create new competency
        competency = Competency(
            name=name,
            description=description,

        )
        
        db.session.add(competency)
        db.session.flush()  # Get the ID of the new competency
        
        # Add behaviors for each level
        for level in range(1, 6):  # Levels 1-5
            behavior_desc = request.form.get(f'level{level}_behavior', '')
            if behavior_desc:
                behavior = CompetencyBehavior(
                    competency_id=competency.id,
                    level=level,
                    description=behavior_desc
                )
                db.session.add(behavior)
        
        db.session.commit()
        flash('Competency created successfully!', 'success')
        return redirect(url_for('competencies.view', id=competency.id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error creating competency: {str(e)}', 'error')
        return redirect(url_for('competencies.create'))

@competencies.route('/<int:id>')
def view(id):
    competency = Competency.query.get_or_404(id)
    behaviors = CompetencyBehavior.query.filter_by(competency_id=id).order_by(CompetencyBehavior.level).all()
    
    # Create a dictionary of behaviors by level for easier access in template
    behaviors_by_level = {behavior.level: behavior for behavior in behaviors}
    
    return render_template('competencies/view.html', 
                          competency=competency, 
                          behaviors=behaviors,
                          behaviors_by_level=behaviors_by_level)

@competencies.route('/<int:id>/edit')
def edit(id):
    competency = Competency.query.get_or_404(id)
    behaviors = CompetencyBehavior.query.filter_by(competency_id=id).all()
    
    # Create a dictionary of behaviors by level for easier access in template
    behaviors_by_level = {behavior.level: behavior for behavior in behaviors}
    
    categories = ['Technical', 'Leadership', 'Interpersonal', 'Business', 'Other']
    
    return render_template('competencies/edit.html', 
                          competency=competency, 
                          behaviors_by_level=behaviors_by_level,
                          categories=categories)

@competencies.route('/<int:id>/update', methods=['POST'])
def update(id):
    try:
        competency = Competency.query.get_or_404(id)
        
        competency.name = request.form['name']
        competency.description = request.form['description']
     
        
        # Update or create behaviors for each level
        for level in range(1, 6):  # Levels 1-5
            behavior_desc = request.form.get(f'level{level}_behavior', '')
            behavior = CompetencyBehavior.query.filter_by(competency_id=id, level=level).first()
            
            if behavior:
                if behavior_desc:
                    behavior.description = behavior_desc
                else:
                    db.session.delete(behavior)
            elif behavior_desc:
                behavior = CompetencyBehavior(
                    competency_id=id,
                    level=level,
                    description=behavior_desc
                )
                db.session.add(behavior)
        
        db.session.commit()
        flash('Competency updated successfully!', 'success')
        return redirect(url_for('competencies.view', id=id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error updating competency: {str(e)}', 'error')
        return redirect(url_for('competencies.edit', id=id))

@competencies.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    try:
        competency = Competency.query.get_or_404(id)
        
        # Check if this competency is used in any job roles
        if competency.role_competencies:
            flash('Cannot delete competency. It is used in one or more job roles.', 'error')
            return redirect(url_for('competencies.view', id=id))
        
        # Delete behaviors first
        CompetencyBehavior.query.filter_by(competency_id=id).delete()
        
        # Delete competency
        db.session.delete(competency)
        db.session.commit()
        
        flash('Competency deleted successfully!', 'success')
        return redirect(url_for('competencies.index'))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting competency: {str(e)}', 'error')
        return redirect(url_for('competencies.view', id=id))
