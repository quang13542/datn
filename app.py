from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_appbuilder import AppBuilder, SQLA
from dotenv import load_dotenv
from flask_migrate import Migrate
from superset import app as superset_app
from metadata import URI, SUPERSET_SECRET_KEY, session
from load_datn.models import (
    DimSkill
)

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.config.from_object('superset_config')

# Initialize SQLAlchemy with Flask-AppBuilder
db = SQLA(app)
migrate = Migrate(app, db)

# Initialize Superset
with app.app_context():
    superset_app.config.update(
        SQLALCHEMY_DATABASE_URI=URI,
        SECRET_KEY=SUPERSET_SECRET_KEY,
    )
    appbuilder = AppBuilder(app, db.session)

@app.route('/home')
def home():
    return 'Hello'

@app.route('/label_skill_category', methods=['GET', 'POST'])
def label_skill_category():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']

        # Find the skill by name and update its category
        skill = DimSkill.query.filter_by(name=name).first()
        if skill:
            skill.category = category
            db.session.commit()
            return redirect(url_for('label_skill_category'))
        else:
            return "Skill not found", 404

    return render_template('label_skill_category.html')

@app.route('/get_skill_names', methods=['GET'])
def get_skill_names():
    skills = session.query(DimSkill).all()
    skill_names = [skill.name for skill in skills]
    return jsonify(skill_names)

if __name__ == '__main__':
    app.run(debug=True)
