# Competency Compass

Competency Compass is an AI-driven competency management and development planning system for organizations. This MVP (Minimum Viable Product) demonstrates the core functionality of the system.

## Features

- Competency framework management
- Department and job role organization
- Employee competency assessment
- Competency gap analysis
- AI-powered development recommendations
- Visual progress tracking

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/competency-compass.git
   cd competency-compass
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add the following:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///competency_compass.db
   OPENAI_API_KEY=your-openai-api-key  # Optional for enhanced AI features
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Access the application in your browser at `http://127.0.0.1:5000/`

## Initial Setup Guide

After installing and running the application, follow these steps to set up your competency framework:

1. **Create Departments**: Set up the organizational structure by adding departments.

2. **Define Competencies**: Create competencies with clear descriptions and behavioral indicators for each proficiency level (1-5).

3. **Create Job Roles**: Define job roles and assign required competencies with specific proficiency levels.

4. **Add Employees**: Add employees and assign them to appropriate job roles.

5. **Conduct Assessments**: Assess employees against the competency requirements for their roles.

6. **Generate Recommendations**: Use the AI feature to generate personalized development recommendations.

7. **Create Development Plans**: Build development plans for employees based on assessment results and recommendations.

## Project Structure

```
competency_compass/
├── app.py                 # Main application file
├── models.py              # Database models
├── routes/                # Route handlers
│   ├── __init__.py
│   ├── departments.py
│   ├── competencies.py
│   ├── job_roles.py
│   ├── employees.py
│   ├── assessments.py
│   ├── development_plans.py
│   └── ai_recommendations.py
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── 404.html
│   ├── 500.html
│   ├── departments/
│   ├── competencies/
│   ├── job_roles/
│   ├── employees/
│   ├── assessments/
│   ├── development_plans/
│   └── ai_recommendations/
├── static/                # Static files (CSS, JS, images)
├── migrations/            # Database migrations
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Charting**: Chart.js
- **AI Integration**: Prepared for OpenAI API integration (mock implementation for MVP)

## Development

### Running Tests

```bash
python -m pytest
```

### Database Migrations

After making changes to the models:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Adding Sample Data

For development and testing purposes, you can populate the database with sample data:

```bash
flask seed
```

## Deployment

### Preparing for Production

1. Update your `.env` file with production settings:
   ```
   FLASK_ENV=production
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

2. Set up a production database (PostgreSQL recommended).

3. Run database migrations:
   ```bash
   flask db upgrade
   ```

4. Configure a production WSGI server (Gunicorn, uWSGI, etc.)

### Docker Deployment

A Dockerfile is provided for containerized deployment:

```bash
docker build -t competency-compass .
docker run -p 5000:5000 competency-compass
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for API integration capabilities
- Flask team for the web framework
- Tailwind CSS for the UI framework
