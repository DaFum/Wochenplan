from . import db


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class PlannerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    subject1_id = db.Column(
        db.Integer, db.ForeignKey('subject.id'), nullable=False
    )
    material1 = db.Column(db.String(100))
    subject2_id = db.Column(
        db.Integer, db.ForeignKey('subject.id'), nullable=False
    )
    material2 = db.Column(db.String(100))
    learning_subject_id = db.Column(
        db.Integer, db.ForeignKey('subject.id'), nullable=False
    )
    learning_task = db.Column(db.String(100))

    __table_args__ = (
        db.UniqueConstraint('day', 'week_start', name='_day_week_uc'),
        db.Index('idx_day', 'day'),
        db.Index('idx_week_start', 'week_start'),
    )

    subject1 = db.relationship('Subject', foreign_keys=[subject1_id])
    subject2 = db.relationship('Subject', foreign_keys=[subject2_id])
    learning_subject = db.relationship(
        'Subject', foreign_keys=[learning_subject_id]
    )


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    priority = db.Column(db.String(20), default='MEDIUM')
    status = db.Column(db.String(20), default='OPEN')
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Task {self.title}>"
