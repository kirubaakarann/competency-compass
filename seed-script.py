from app import app, db
from models import Department, Competency, CompetencyBehavior, JobRole, RoleCompetency, Employee
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with sample data for development and testing."""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Employee.query.delete()
        RoleCompetency.query.delete()
        JobRole.query.delete()
        CompetencyBehavior.query.delete()
        Competency.query.delete()
        Department.query.delete()
        
        # Create departments
        print("Creating departments...")
        departments = [
            Department(name="Engineering", description="Software development and technical operations team."),
            Department(name="Marketing", description="Responsible for brand management and market strategy."),
            Department(name="Sales", description="Revenue generation and customer acquisition."),
            Department(name="Human Resources", description="People management and organizational development.")
        ]
        db.session.add_all(departments)
        db.session.commit()
        
        # Create competencies
        print("Creating competencies...")
        competencies = [
            # Technical competencies
            Competency(name="Software Development", description="Ability to design and build software applications.", category="Technical"),
            Competency(name="Data Analysis", description="Skills in interpreting data and deriving insights.", category="Technical"),
            Competency(name="Technical Troubleshooting", description="Ability to diagnose and resolve technical issues.", category="Technical"),
            
            # Leadership competencies
            Competency(name="Strategic Thinking", description="Ability to develop long-term objectives and plans.", category="Leadership"),
            Competency(name="Team Leadership", description="Ability to lead and motivate a team.", category="Leadership"),
            Competency(name="Decision Making", description="Ability to make effective and timely decisions.", category="Leadership"),
            
            # Interpersonal competencies
            Competency(name="Communication", description="Ability to convey information effectively.", category="Interpersonal"),
            Competency(name="Collaboration", description="Ability to work effectively with others.", category="Interpersonal"),
            Competency(name="Customer Focus", description="Dedication to meeting customer expectations.", category="Interpersonal"),
            
            # Business competencies
            Competency(name="Business Acumen", description="Understanding of business operations and economics.", category="Business"),
            Competency(name="Project Management", description="Ability to plan, execute, and close projects.", category="Business"),
            Competency(name="Innovation", description="Ability to introduce new ideas or methods.", category="Business")
        ]
        db.session.add_all(competencies)
        db.session.commit()
        
        # Create competency behaviors
        print("Creating competency behaviors...")
        for competency in competencies:
            for level in range(1, 6):
                description = f"Level {level} behavior for {competency.name}: "
                
                if level == 1:
                    description += "Basic awareness and understanding of fundamental concepts."
                elif level == 2:
                    description += "Ability to apply knowledge with guidance in routine situations."
                elif level == 3:
                    description += "Independent application of skills in standard situations with good results."
                elif level == 4:
                    description += "Advanced application with the ability to handle complex situations and guide others."
                elif level == 5:
                    description += "Expert-level mastery with the ability to develop new approaches and drive innovation."
                
                behavior = CompetencyBehavior(
                    competency_id=competency.id,
                    level=level,
                    description=description
                )
                db.session.add(behavior)
        
        db.session.commit()
        
        # Create job roles
        print("Creating job roles...")
        job_roles = [
            # Engineering roles
            JobRole(title="Software Engineer", description="Designs and builds software applications.", department_id=departments[0].id),
            JobRole(title="Engineering Manager", description="Leads a team of engineers.", department_id=departments[0].id),
            JobRole(title="QA Engineer", description="Ensures software quality through testing.", department_id=departments[0].id),
            
            # Marketing roles
            JobRole(title="Marketing Specialist", description="Executes marketing campaigns and initiatives.", department_id=departments[1].id),
            JobRole(title="Marketing Manager", description="Leads marketing strategy and team.", department_id=departments[1].id),
            
            # Sales roles
            JobRole(title="Sales Representative", description="Sells products and services to customers.", department_id=departments[2].id),
            JobRole(title="Sales Manager", description="Leads sales team and strategy.", department_id=departments[2].id),
            
            # HR roles
            JobRole(title="HR Specialist", description="Supports HR functions and employee needs.", department_id=departments[3].id),
            JobRole(title="HR Manager", description="Leads HR strategy and initiatives.", department_id=departments[3].id)
        ]
        db.session.add_all(job_roles)
        db.session.commit()
        
        # Create role competencies
        print("Creating role competencies...")
        role_competency_mappings = [
            # Software Engineer
            {"role_id": job_roles[0].id, "comp_id": competencies[0].id, "level": 4, "weight": 10},  # Software Development
            {"role_id": job_roles[0].id, "comp_id": competencies[2].id, "level": 3, "weight": 8},   # Technical Troubleshooting
            {"role_id": job_roles[0].id, "comp_id": competencies[7].id, "level": 3, "weight": 7},   # Collaboration
            {"role_id": job_roles[0].id, "comp_id": competencies[10].id, "level": 2, "weight": 5},  # Project Management
            
            # Engineering Manager
            {"role_id": job_roles[1].id, "comp_id": competencies[0].id, "level": 4, "weight": 8},   # Software Development
            {"role_id": job_roles[1].id, "comp_id": competencies[4].id, "level": 4, "weight": 10},  # Team Leadership
            {"role_id": job_roles[1].id, "comp_id": competencies[5].id, "level": 4, "weight": 9},   # Decision Making
            {"role_id": job_roles[1].id, "comp_id": competencies[6].id, "level": 4, "weight": 8},   # Communication
            {"role_id": job_roles[1].id, "comp_id": competencies[10].id, "level": 4, "weight": 7},  # Project Management
            
            # QA Engineer
            {"role_id": job_roles[2].id, "comp_id": competencies[2].id, "level": 4, "weight": 10},  # Technical Troubleshooting
            {"role_id": job_roles[2].id, "comp_id": competencies[7].id, "level": 3, "weight": 7},   # Collaboration
            {"role_id": job_roles[2].id, "comp_id": competencies[8].id, "level": 3, "weight": 8},   # Customer Focus
            
            # Marketing Specialist
            {"role_id": job_roles[3].id, "comp_id": competencies[1].id, "level": 3, "weight": 8},   # Data Analysis
            {"role_id": job_roles[3].id, "comp_id": competencies[6].id, "level": 4, "weight": 9},   # Communication
            {"role_id": job_roles[3].id, "comp_id": competencies[8].id, "level": 4, "weight": 9},   # Customer Focus
            {"role_id": job_roles[3].id, "comp_id": competencies[11].id, "level": 3, "weight": 7},  # Innovation
            
            # Marketing Manager
            {"role_id": job_roles[4].id, "comp_id": competencies[3].id, "level": 4, "weight": 10},  # Strategic Thinking
            {"role_id": job_roles[4].id, "comp_id": competencies[4].id, "level": 4, "weight": 9},   # Team Leadership
            {"role_id": job_roles[4].id, "comp_id": competencies[6].id, "level": 4, "weight": 8},   # Communication
            {"role_id": job_roles[4].id, "comp_id": competencies[9].id, "level": 3, "weight": 7},   # Business Acumen
            {"role_id": job_roles[4].id, "comp_id": competencies[11].id, "level": 4, "weight": 9},  # Innovation
            
            # Sales Representative
            {"role_id": job_roles[5].id, "comp_id": competencies[6].id, "level": 4, "weight": 10},  # Communication
            {"role_id": job_roles[5].id, "comp_id": competencies[8].id, "level": 5, "weight": 10},  # Customer Focus
            {"role_id": job_roles[5].id, "comp_id": competencies[9].id, "level": 3, "weight": 7},   # Business Acumen
            
            # Sales Manager
            {"role_id": job_roles[6].id, "comp_id": competencies[3].id, "level": 4, "weight": 8},   # Strategic Thinking
            {"role_id": job_roles[6].id, "comp_id": competencies[4].id, "level": 4, "weight": 9},   # Team Leadership
            {"role_id": job_roles[6].id, "comp_id": competencies[6].id, "level": 4, "weight": 8},   # Communication
            {"role_id": job_roles[6].id, "comp_id": competencies[8].id, "level": 4, "weight": 9},   # Customer Focus
            {"role_id": job_roles[6].id, "comp_id": competencies[9].id, "level": 4, "weight": 8},   # Business Acumen
            
            # HR Specialist
            {"role_id": job_roles[7].id, "comp_id": competencies[6].id, "level": 4, "weight": 9},   # Communication
            {"role_id": job_roles[7].id, "comp_id": competencies[7].id, "level": 4, "weight": 8},   # Collaboration
            {"role_id": job_roles[7].id, "comp_id": competencies[8].id, "level": 3, "weight": 7},   # Customer Focus
            
            # HR Manager
            {"role_id": job_roles[8].id, "comp_id": competencies[3].id, "level": 3, "weight": 7},   # Strategic Thinking
            {"role_id": job_roles[8].id, "comp_id": competencies[4].id, "level": 4, "weight": 9},   # Team Leadership
            {"role_id": job_roles[8].id, "comp_id": competencies[5].id, "level": 4, "weight": 8},   # Decision Making
            {"role_id": job_roles[8].id, "comp_id": competencies[6].id, "level": 4, "weight": 9},   # Communication
            {"role_id": job_roles[8].id, "comp_id": competencies[9].id, "level": 3, "weight": 6}    # Business Acumen
        ]
        
        for mapping in role_competency_mappings:
            role_comp = RoleCompetency(
                job_role_id=mapping["role_id"],
                competency_id=mapping["comp_id"],
                required_level=mapping["level"],
                weight=mapping["weight"]
            )
            db.session.add(role_comp)
        
        db.session.commit()
        
        # Create employees
        print("Creating employees...")
        employees = [
            # Engineering
            Employee(name="John Smith", email="john.smith@example.com", job_role_id=job_roles[0].id, 
                    hire_date=datetime.now() - timedelta(days=365*2)),
            Employee(name="Emily Johnson", email="emily.johnson@example.com", job_role_id=job_roles[1].id,
                    hire_date=datetime.now() - timedelta(days=365*4)),
            Employee(name="Michael Brown", email="michael.brown@example.com", job_role_id=job_roles[0].id,
                    hire_date=datetime.now() - timedelta(days=365*1)),
            Employee(name="Sarah Davis", email="sarah.davis@example.com", job_role_id=job_roles[2].id,
                    hire_date=datetime.now() - timedelta(days=365*3)),
            
            # Marketing
            Employee(name="David Wilson", email="david.wilson@example.com", job_role_id=job_roles[3].id,
                    hire_date=datetime.now() - timedelta(days=365*2)),
            Employee(name="Jessica Martinez", email="jessica.martinez@example.com", job_role_id=job_roles[4].id,
                    hire_date=datetime.now() - timedelta(days=365*5)),
            
            # Sales
            Employee(name="Robert Taylor", email="robert.taylor@example.com", job_role_id=job_roles[5].id,
                    hire_date=datetime.now() - timedelta(days=365*1.5)),
            Employee(name="Jennifer Anderson", email="jennifer.anderson@example.com", job_role_id=job_roles[6].id,
                    hire_date=datetime.now() - timedelta(days=365*4)),
            
            # HR
            Employee(name="Thomas Clark", email="thomas.clark@example.com", job_role_id=job_roles[7].id,
                    hire_date=datetime.now() - timedelta(days=365*2.5)),
            Employee(name="Lisa Rodriguez", email="lisa.rodriguez@example.com", job_role_id=job_roles[8].id,
                    hire_date=datetime.now() - timedelta(days=365*6))
        ]
        db.session.add_all(employees)
        db.session.commit()
        
        print("Seeding complete!")

if __name__ == "__main__":
    seed_database()
