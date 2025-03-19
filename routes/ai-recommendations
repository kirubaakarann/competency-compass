from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Employee, JobRole, Competency, RoleCompetency, AIRecommendation, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
import random
import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API (mock setup for MVP)
openai.api_key = os.getenv("OPENAI_API_KEY", "mock-key-for-demo")

ai_recommendations = Blueprint('ai_recommendations', __name__)

@ai_recommendations.route('/')
def index():
    employees = Employee.query.all()
    return render_template('ai_recommendations/index.html', employees=employees)

@ai_recommendations.route('/generate/<int:employee_id>', methods=['GET'])
def generate(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    job_role = employee.job_role
    
    # Get all competencies required for the job role
    role_competencies = RoleCompetency.query.filter_by(job_role_id=job_role.id).all()
    
    # Get employee's current ratings for each competency
    employee_ratings = {}
    for rc in role_competencies:
        # This would normally be fetched from the assessment ratings
        # For MVP, we'll generate random ratings if none exist
        rating = random.randint(1, 5)  # Mock rating for demo
        employee_ratings[rc.competency_id] = rating
    
    # Identify gaps (where employee rating < required level)
    competency_gaps = []
    for rc in role_competencies:
        employee_rating = employee_ratings.get(rc.competency_id, 0)
        if employee_rating < rc.required_level:
            gap = {
                'competency_id': rc.competency_id,
                'competency_name': rc.competency.name,
                'current_level': employee_rating,
                'required_level': rc.required_level,
                'gap': rc.required_level - employee_rating,
                'weight': rc.weight
            }
            competency_gaps.append(gap)
    
    # Sort gaps by weight and gap size to prioritize
    competency_gaps.sort(key=lambda x: (x['weight'], x['gap']), reverse=True)
    
    # Get existing recommendations
    existing_recommendations = AIRecommendation.query.filter_by(employee_id=employee_id).all()
    
    return render_template('ai_recommendations/generate.html', 
                          employee=employee, 
                          job_role=job_role,
                          competency_gaps=competency_gaps,
                          existing_recommendations=existing_recommendations)

@ai_recommendations.route('/api/generate/<int:employee_id>/<int:competency_id>', methods=['POST'])
def api_generate_recommendation(employee_id, competency_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        competency = Competency.query.get_or_404(competency_id)
        
        # Get the job role and required level
        job_role = employee.job_role
        role_competency = RoleCompetency.query.filter_by(
            job_role_id=job_role.id, 
            competency_id=competency_id
        ).first_or_404()
        
        # Mock employee's current level for demo
        current_level = random.randint(1, role_competency.required_level-1) if role_competency.required_level > 1 else 1
        
        # Get behaviors for current and target levels
        current_behaviors = competency.behaviors_by_level(current_level)
        target_behaviors = competency.behaviors_by_level(role_competency.required_level)
        
        # In a real implementation, we would call the OpenAI API here
        # For MVP, we'll use pre-defined recommendations
        
        recommendation_types = [
            "Training Course", 
            "Book/Article", 
            "Practical Exercise", 
            "Mentoring", 
            "Online Resource"
        ]
        
        # Generate mock recommendations
        recommendations = []
        for _ in range(3):  # Generate 3 recommendations
            rec_type = random.choice(recommendation_types)
            
            if rec_type == "Training Course":
                content = generate_training_recommendation(competency.name, current_level, role_competency.required_level)
            elif rec_type == "Book/Article":
                content = generate_reading_recommendation(competency.name, current_level, role_competency.required_level)
            elif rec_type == "Practical Exercise":
                content = generate_exercise_recommendation(competency.name, current_level, role_competency.required_level)
            elif rec_type == "Mentoring":
                content = generate_mentoring_recommendation(competency.name, current_level, role_competency.required_level)
            else:  # Online Resource
                content = generate_online_recommendation(competency.name, current_level, role_competency.required_level)
            
            # Save recommendation to database
            recommendation = AIRecommendation(
                employee_id=employee_id,
                competency_id=competency_id,
                recommendation_type=rec_type,
                content=content
            )
            db.session.add(recommendation)
            recommendations.append({
                'type': rec_type,
                'content': content
            })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'message': f"Generated {len(recommendations)} recommendations for {competency.name}"
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f"Error generating recommendations: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

@ai_recommendations.route('/recommendations/<int:employee_id>')
def employee_recommendations(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    recommendations = AIRecommendation.query.filter_by(employee_id=employee_id).all()
    
    # Group recommendations by competency
    grouped_recommendations = {}
    for rec in recommendations:
        if rec.competency_id not in grouped_recommendations:
            grouped_recommendations[rec.competency_id] = {
                'competency': rec.competency,
                'recommendations': []
            }
        grouped_recommendations[rec.competency_id]['recommendations'].append(rec)
    
    return render_template('ai_recommendations/recommendations.html', 
                          employee=employee, 
                          grouped_recommendations=grouped_recommendations)

@ai_recommendations.route('/apply/<int:recommendation_id>', methods=['POST'])
def apply_recommendation(recommendation_id):
    try:
        recommendation = AIRecommendation.query.get_or_404(recommendation_id)
        recommendation.is_applied = True
        db.session.commit()
        
        flash(f'Recommendation added to development plan successfully!', 'success')
        return redirect(url_for('ai_recommendations.employee_recommendations', employee_id=recommendation.employee_id))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error applying recommendation: {str(e)}', 'error')
        return redirect(url_for('ai_recommendations.index'))

# Helper functions to generate recommendations
def generate_training_recommendation(competency_name, current_level, target_level):
    training_options = {
        "Leadership": [
            "Advanced Leadership Skills Workshop",
            "Strategic Leadership Masterclass",
            "Leadership Communication Excellence",
            "Leading High-Performance Teams",
            "Emotional Intelligence for Leaders"
        ],
        "Technical": [
            "Advanced Technical Skills Bootcamp",
            "Technical Certification Program",
            "Hands-on Technical Lab Workshop",
            "Technical Problem-Solving Masterclass",
            "Technical Architecture Fundamentals"
        ],
        "Interpersonal": [
            "Effective Communication Workshop",
            "Conflict Resolution Skills",
            "Building Professional Relationships",
            "Negotiation and Influence",
            "Team Collaboration Skills"
        ],
        "Business": [
            "Business Strategy Fundamentals",
            "Financial Acumen for Professionals",
            "Business Process Optimization",
            "Strategic Decision Making",
            "Business Innovation Workshop"
        ]
    }
    
    category = "Leadership"  # Default
    for key in training_options.keys():
        if key.lower() in competency_name.lower():
            category = key
            break
    
    course = random.choice(training_options.get(category, training_options["Leadership"]))
    
    return f"Complete the '{course}' training course to develop your {competency_name} skills from level {current_level} to level {target_level}. This structured learning program will provide you with practical techniques and frameworks to enhance your capabilities."

def generate_reading_recommendation(competency_name, current_level, target_level):
    reading_options = {
        "Leadership": [
            "Leadership in Turbulent Times by Doris Kearns Goodwin",
            "Start with Why by Simon Sinek",
            "Dare to Lead by Brené Brown",
            "The 21 Irrefutable Laws of Leadership by John C. Maxwell",
            "Good to Great by Jim Collins"
        ],
        "Technical": [
            "The Phoenix Project by Gene Kim",
            "Clean Code by Robert C. Martin",
            "Designing Data-Intensive Applications by Martin Kleppmann",
            "The Pragmatic Programmer by Andrew Hunt",
            "Site Reliability Engineering: How Google Runs Production Systems"
        ],
        "Interpersonal": [
            "Crucial Conversations by Kerry Patterson",
            "How to Win Friends and Influence People by Dale Carnegie",
            "Emotional Intelligence 2.0 by Travis Bradberry",
            "Nonviolent Communication by Marshall B. Rosenberg",
            "Never Split the Difference by Chris Voss"
        ],
        "Business": [
            "The Lean Startup by Eric Ries",
            "Blue Ocean Strategy by W. Chan Kim",
            "Thinking, Fast and Slow by Daniel Kahneman",
            "The Innovator's Dilemma by Clayton Christensen",
            "Zero to One by Peter Thiel"
        ]
    }
    
    category = "Leadership"  # Default
    for key in reading_options.keys():
        if key.lower() in competency_name.lower():
            category = key
            break
    
    book = random.choice(reading_options.get(category, reading_options["Leadership"]))
    
    return f"Read '{book}' to strengthen your understanding of {competency_name} concepts and principles. This resource will provide valuable insights to help you progress from level {current_level} to level {target_level}."

def generate_exercise_recommendation(competency_name, current_level, target_level):
    exercise_templates = [
        "Create a personal development project where you {action} to practice your {competency} skills. Document your progress and reflect on challenges encountered.",
        "Volunteer to {action} in your next team project to build your {competency} capabilities. Set specific goals to move from level {current} to {target}.",
        "Design and complete a series of small challenges that require you to {action}. Start with simpler tasks and gradually increase complexity.",
        "Partner with a colleague to practice {competency} skills by {action}. Give each other feedback to identify improvement opportunities.",
        "Develop a 30-day challenge where you {action} daily to strengthen your {competency} muscles."
    ]
    
    actions = {
        "Leadership": [
            "lead a cross-functional initiative", 
            "facilitate team decision-making", 
            "develop a strategic vision", 
            "mentor a junior team member",
            "lead a process improvement initiative"
        ],
        "Technical": [
            "build a proof-of-concept solution", 
            "optimize existing systems", 
            "document technical processes", 
            "troubleshoot complex problems",
            "implement new technical standards"
        ],
        "Interpersonal": [
            "facilitate difficult conversations", 
            "practice active listening techniques", 
            "provide constructive feedback", 
            "build consensus among diverse stakeholders",
            "navigate conflict situations productively"
        ],
        "Business": [
            "analyze business metrics", 
            "develop a business case", 
            "map value streams", 
            "identify process inefficiencies",
            "propose data-driven solutions"
        ]
    }
    
    category = "Leadership"  # Default
    for key in actions.keys():
        if key.lower() in competency_name.lower():
            category = key
            break
    
    action = random.choice(actions.get(category, actions["Leadership"]))
    template = random.choice(exercise_templates)
    
    return template.format(
        action=action, 
        competency=competency_name, 
        current=current_level, 
        target=target_level
    )

def generate_mentoring_recommendation(competency_name, current_level, target_level):
    mentoring_templates = [
        "Arrange regular mentoring sessions with {mentor_type} to develop your {competency} skills. Focus specifically on {focus_area}.",
        "Shadow {mentor_type} during {activity} to observe effective {competency} practices. Debrief afterward to discuss key takeaways.",
        "Request feedback from {mentor_type} on your {competency} approach. Use their insights to create a targeted improvement plan.",
        "Establish a coaching relationship with {mentor_type} who excels in {competency}. Meet bi-weekly to review progress and challenges.",
        "Join a community of practice led by {mentor_type} to enhance your {competency} capabilities through group learning."
    ]
    
    mentor_types = {
        "Leadership": [
            "a senior leader in your organization", 
            "an experienced manager", 
            "a leadership coach", 
            "a cross-functional leader",
            "an executive with strong leadership skills"
        ],
        "Technical": [
            "a technical expert in your field", 
            "a senior engineer or architect", 
            "a technical specialist", 
            "a solutions architect",
            "an industry-recognized technical authority"
        ],
        "Interpersonal": [
            "a colleague known for strong people skills", 
            "a communication specialist", 
            "a team facilitator", 
            "a relationship-builder in your network",
            "a professional coach focused on interpersonal skills"
        ],
        "Business": [
            "a business strategist", 
            "a product or portfolio manager", 
            "a business operations expert", 
            "an experienced business analyst",
            "a senior stakeholder with business acumen"
        ]
    }
    
    focus_areas = {
        "Leadership": [
            "strategic thinking", 
            "team motivation", 
            "delegating effectively", 
            "managing stakeholder expectations",
            "leading through change"
        ],
        "Technical": [
            "technical design decisions", 
            "code quality and standards", 
            "system architecture", 
            "technical troubleshooting",
            "technical knowledge transfer"
        ],
        "Interpersonal": [
            "handling difficult conversations", 
            "building rapport", 
            "reading non-verbal cues", 
            "adapting communication style",
            "building trust with diverse colleagues"
        ],
        "Business": [
            "business case development", 
            "financial analysis", 
            "process optimization", 
            "market trend analysis",
            "business value delivery"
        ]
    }
    
    activities = {
        "Leadership": [
            "leadership meetings", 
            "team planning sessions", 
            "stakeholder negotiations", 
            "performance reviews",
            "strategic planning workshops"
        ],
        "Technical": [
            "system design sessions", 
            "code reviews", 
            "architecture discussions", 
            "technical problem-solving",
            "technical planning sessions"
        ],
        "Interpersonal": [
            "team facilitations", 
            "conflict resolution discussions", 
            "client presentations", 
            "team-building activities",
            "cross-functional collaborations"
        ],
        "Business": [
            "business planning meetings", 
            "customer discovery sessions", 
            "financial reviews", 
            "process improvement workshops",
            "strategy sessions"
        ]
    }
    
    category = "Leadership"  # Default
    for key in mentor_types.keys():
        if key.lower() in competency_name.lower():
            category = key
            break
    
    mentor_type = random.choice(mentor_types.get(category, mentor_types["Leadership"]))
    focus_area = random.choice(focus_areas.get(category, focus_areas["Leadership"]))
    activity = random.choice(activities.get(category, activities["Leadership"]))
    template = random.choice(mentoring_templates)
    
    return template.format(
        mentor_type=mentor_type, 
        competency=competency_name, 
        focus_area=focus_area,
        activity=activity
    )

def generate_online_recommendation(competency_name, current_level, target_level):
    online_templates = [
        "Complete the online course '{course_name}' on {platform} to develop your {competency} skills from level {current} to {target}.",
        "Join the '{community_name}' online community to learn {competency} best practices from practitioners worldwide.",
        "Subscribe to the '{resource_name}' newsletter/podcast for regular insights on {competency} topics relevant to your development needs.",
        "Participate in the virtual workshop series '{workshop_name}' to build practical {competency} skills through interactive exercises.",
        "Use the '{tool_name}' online tool/platform to practice and reinforce your {competency} skills with real-world scenarios."
    ]
    
    courses = {
        "Leadership": [
            "Leadership Fundamentals", 
            "Strategic Leadership in Practice", 
            "Leading High-Performance Teams", 
            "Emotional Intelligence for Leaders",
            "Adaptive Leadership"
        ],
        "Technical": [
            "Advanced Technical Architecture", 
            "Technical Problem-Solving Masterclass", 
            "System Design and Architecture", 
            "Technical Best Practices",
            "Expert Troubleshooting Techniques"
        ],
        "Interpersonal": [
            "Communication Strategies for Professionals", 
            "Building Effective Relationships", 
            "Conflict Resolution in the Workplace", 
            "Influencing Without Authority",
            "Collaborative Problem-Solving"
        ],
        "Business": [
            "Business Strategy Fundamentals", 
            "Data-Driven Decision Making", 
            "Business Process Optimization", 
            "Financial Acumen for Professionals",
            "Strategic Business Planning"
        ]
    }
    
    platforms = [
        "LinkedIn Learning", 
        "Coursera", 
        "Udemy", 
        "edX", 
        "Pluralsight"
    ]
    
    communities = {
        "Leadership": [
            "Leadership Connect", 
            "Leaders Forum", 
            "Executive Mindshare", 
            "Leadership Development Network",
            "Global Leadership Community"
        ],
        "Technical": [
            "Tech Excellence Network", 
            "Developer Community", 
            "Architecture Guild", 
            "Engineering Excellence Forum",
            "Technical Mastery Group"
        ],
        "Interpersonal": [
            "Communication Professionals", 
            "Relationship Builders Network", 
            "Influencers Guild", 
            "Collaboration Community",
            "People Skills Collective"
        ],
        "Business": [
            "Business Strategy Network", 
            "Innovation Hub", 
            "Business Excellence Community", 
            "Strategic Thinkers Forum",
            "Business Transformation Group"
        ]
    }
    
    resources = {
        "Leadership": [
            "Leadership Insights", 
            "Leading Teams", 
            "Executive Perspective", 
            "Leadership Today",
            "The Leadership Coach"
        ],
        "Technical": [
            "Tech Deep Dive", 
            "Code Masters", 
            "Architecture Weekly", 
            "Technical Excellence",
            "The Developer's Toolkit"
        ],
        "Interpersonal": [
            "Communication Matters", 
            "People Skills Today", 
            "The Empathy Effect", 
            "Connection Catalyst",
            "Relationship Intelligence"
        ],
        "Business": [
            "Business Strategy Review", 
            "Innovation Insider", 
            "Process Optimization Journal", 
            "Strategic Business Today",
            "The Business Analyst"
        ]
    }
    
    category = "Leadership"  # Default
    for key in courses.keys():
        if key.lower() in competency_name.lower():
            category = key
            break
    
    course_name = random.choice(courses.get(category, courses["Leadership"]))
    platform = random.choice(platforms)
    community_name = random.choice(communities.get(category, communities["Leadership"]))
    resource_name = random.choice(resources.get(category, resources["Leadership"]))
    workshop_name = f"{competency_name} Mastery Workshop"
    tool_name = f"{competency_name} Simulator"
    
    template = random.choice(online_templates)
    
    return template.format(
        course_name=course_name,
        platform=platform,
        community_name=community_name,
        resource_name=resource_name,
        workshop_name=workshop_name,
        tool_name=tool_name,
        competency=competency_name,
        current=current_level,
        target=target_level
    )
