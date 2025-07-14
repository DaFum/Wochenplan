from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Subject

class PlannerForm(FlaskForm):
    subject1 = QuerySelectField('Fach 1', query_factory=lambda: Subject.query.all(), get_label='name')
    material1 = StringField('Material 1', render_kw={"placeholder": "Material 1"})
    subject2 = QuerySelectField('Fach 2', query_factory=lambda: Subject.query.all(), get_label='name')
    material2 = StringField('Material 2', render_kw={"placeholder": "Material 2"})
    learning_subject = QuerySelectField('Lernfach', query_factory=lambda: Subject.query.all(), get_label='name')
    learning_task = StringField('Lernaufgabe', render_kw={"placeholder": "Lernaufgabe"})
    submit = SubmitField('Speichern')
