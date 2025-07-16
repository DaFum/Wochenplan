from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class PlannerForm(FlaskForm):
    learning_subject = SelectField('Lernfach', validators=[DataRequired()])
    learning_task = StringField('Lernaufgabe', validators=[DataRequired()], render_kw={"placeholder": "Lernaufgabe"})
    submit = SubmitField('Speichern')
