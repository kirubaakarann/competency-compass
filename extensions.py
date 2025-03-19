from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()
migrate = Migrate()
