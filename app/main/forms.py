from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Optional

from app.models import TaskPriority


class PlannerForm(FlaskForm):
    learning_subject = SelectField('Lernfach', validators=[DataRequired()])
    learning_task = StringField(
        'Lernaufgabe',
        validators=[DataRequired()],
        render_kw={"placeholder": "Lernaufgabe", "list": "taskSuggestions"}
    )
    due_date = DateTimeLocalField(
        'Fälligkeitsdatum',
        validators=[Optional()],
        format='%Y-%m-%dT%H:%M'
    )
    priority = SelectField(
        'Priorität',
        choices=[(p.name, p.value) for p in TaskPriority],
        default=TaskPriority.MEDIUM.name,
        validators=[DataRequired()]
    )
    submit = SubmitField('Speichern')


class SubjectForm(FlaskForm):
    new_subject = StringField(
        'Neues Fach',
        validators=[DataRequired()],
        render_kw={"placeholder": "Fach hinzufügen"}
    )
    submit = SubmitField('Fach hinzufügen')
