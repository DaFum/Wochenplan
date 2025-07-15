from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class PlannerForm(FlaskForm):
    learning_task = StringField('Lernaufgabe', validators=[DataRequired()], render_kw={"placeholder": "Lernaufgabe"})
    submit = SubmitField('Speichern')
