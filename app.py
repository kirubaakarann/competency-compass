from flask import Flask, render_template, redirect, url_for, flash, session
from models.models import db, Department, Competency, JobRole, Employee
from routes.job_roles import job_roles
from routes.competencies import competencies
from routes.employees import employees
from routes.assessments import assessments
from routes.development_plans import development_plans
from routes.ai_recommendations import ai_recommendations
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///competency_compass.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(job_roles, url_prefix='/job-roles')
app.register_blueprint(competencies, url_prefix='/competencies')
app.register_blueprint(employees, url_prefix='/employees')
app.register_blueprint(assessments, url_prefix='/assessments')
app.register_blueprint(development_plans, url_prefix='/development-plans')
app.register_blueprint(ai_recommendations, url_prefix='/ai-recommendations')

@app.route('/')
def index():
    departments_count = Department.query.count()
    competencies_count = Competency.query.count()
    job_roles_count = JobRole.query.count()
    employees_count = Employee.query.count()
    
    return render_template('dashboard.html', 
                          departments_count=departments_count,
                          competencies_count=competencies_count,
                          job_roles_count=job_roles_count,
                          employees_count=employees_count)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
