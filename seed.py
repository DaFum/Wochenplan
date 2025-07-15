from app import create_app, db
from app.models import Subject

def seed_subjects():
    """Seeds the database with initial subjects."""
    app = create_app()
    with app.app_context():
        subjects = [
            "Mathematik",
            "Deutsch",
            "Englisch",
            "Geschichte",
            "Biologie",
            "Chemie",
            "Physik",
            "Kunst",
            "Musik",
            "Sport"
        ]
        for subject_name in subjects:
            if not Subject.query.filter_by(name=subject_name).first():
                subject = Subject(name=subject_name)
                db.session.add(subject)
        db.session.commit()

if __name__ == '__main__':
    seed_subjects()
