from flask import Blueprint, render_template, jsonify, current_app
from models import Employee, JobRole, Competency, Assessment
from extensions import db
import openai
import json

ai_recommendations = Blueprint('ai_recommendations', __name__)

@ai_recommendations.route('/generate/<int:employee_id>')
def generate_recommendations(employee_id):
    # Fetch employee with related data
    employee = Employee.query.get_or_404(employee_id)
    job_role = employee.job_role
    
    # Get assessments and competencies for this employee and job role
    assessments = Assessment.query.filter_by(employee_id=employee_id).all()

    # Calculate competency gaps
    competency_gaps = []
    for competency in job_role.competencies:
        assessment = next((a for a in assessments if a.competency_id == competency.id), None)
        
        if assessment:
            current_level = assessment.current_level
            required_level = competency.required_level
            
            if current_level < required_level:
                competency_gaps.append({
                    'competency_id': competency.id,
                    'competency_name': competency.name,
                    'current_level': current_level,
                    'required_level': required_level,
                    'gap': required_level - current_level
                })

    # Sort gaps by size (largest gaps first)
    competency_gaps.sort(key=lambda x: x['gap'], reverse=True)
    
    return render_template(
        'ai_recommendations/generate.html', 
        employee=employee, 
        job_role=job_role,
        competency_gaps=competency_gaps
    )

@ai_recommendations.route('/api/generate/<int:employee_id>/<int:competency_id>', methods=['POST'])
def generate_competency_recommendations(employee_id, competency_id):
    try:
        # Fetch necessary data
        employee = Employee.query.get_or_404(employee_id)
        competency = Competency.query.get_or_404(competency_id)
        assessment = Assessment.query.filter_by(
            employee_id=employee_id, 
            competency_id=competency_id
        ).first()
        
        # Prepare prompt for AI
        prompt = f"""
        Generate personalized professional development recommendations for an {employee.job_role.title} 
        to improve their {competency.name} competency.

        Current skill level: {assessment.current_level}/5
        Required skill level: {competency.required_level}/5
        
        Provide 3-4 specific, actionable recommendations that can help bridge this competency gap. 
        Each recommendation should:
        - Be specific and targeted to the competency
        - Offer a clear development activity
        - Be realistic and achievable
        
        Format the recommendations as a JSON array with 'type' and 'content' fields.
        """
        
        # Call OpenAI API (error handling included)
        openai.api_key = current_app.config['OPENAI_API_KEY']
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a professional career development advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Extract and parse recommendations
        recommendations_str = response.choices[0].message.content
        recommendations = json.loads(recommendations_str)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        current_app.logger.error(f"Recommendation generation error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Failed to generate recommendations. Please try again.'
        }), 500

@ai_recommendations.route('/recommendations/<int:employee_id>')
def employee_recommendations(employee_id):
    # Fetch employee with related data
    employee = Employee.query.get_or_404(employee_id)
    
    # Fetch all assessments with competency details
    assessments = Assessment.query.filter_by(employee_id=employee_id).all()
    
    # Prepare comprehensive recommendations data
    recommendations_data = []
    for assessment in assessments:
        if assessment.current_level < assessment.competency.required_level:
            # Generate recommendations for this competency
            # In a real app, you'd cache or store these recommendations
            try:
                recommendations_data.append({
                    'competency_name': assessment.competency.name,
                    'current_level': assessment.current_level,
                    'required_level': assessment.competency.required_level,
                    'recommendations': _generate_competency_recommendations(
                        employee, 
                        assessment.competency
                    )
                })
            except Exception as e:
                current_app.logger.error(f"Recommendation generation error: {str(e)}")
    
    return render_template(
        'ai_recommendations/recommendations.html', 
        employee=employee, 
        recommendations_data=recommendations_data
    )

def _generate_competency_recommendations(employee, competency):
    # Internal helper method to generate recommendations
    # This would call the OpenAI API similar to the route method
    # Simplified for brevity
    prompt = f"""
    Generate personalized professional development recommendations for an {employee.job_role.title} 
    to improve their {competency.name} competency.
    """
    
    openai.api_key = current_app.config['OPENAI_API_KEY']
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a professional career development advisor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )
    
    recommendations_str = response.choices[0].message.content
    return json.loads(recommendations_str)

@ai_recommendations.route('/')
def index():
    return render_template('ai_recommendations/index.html')
