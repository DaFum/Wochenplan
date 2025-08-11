from flask_wtf import FlaskForm
from wtforms import (
    DateTimeLocalField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional

from app.modules.task_manager import TaskPriority


class PlannerForm(FlaskForm):
    learning_subject = SelectField('Lernfach', validators=[DataRequired()])
    learning_task = StringField(
        'Lernaufgabe',
        validators=[DataRequired()],
        render_kw={"placeholder": "Lernaufgabe", "list": "taskSuggestions"}
    )
    due_date = DateTimeLocalField(
        'Fällig am',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()],
        render_kw={"type": "datetime-local"},
    )
    priority = SelectField(
        'Priorität',
        choices=[(p.name, p.name.title()) for p in TaskPriority],
        default=TaskPriority.MEDIUM.name,
    )
    submit = SubmitField('Speichern')


class SubjectForm(FlaskForm):
    new_subject = StringField('Neues Fach', validators=[DataRequired()])
    submit = SubmitField('Hinzufügen')
