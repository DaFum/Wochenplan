from app import create_app, db
from app.models import Subject


def seed_subjects():
    """
    Fügt der Datenbank eine vordefinierte Liste von Schulfächern hinzu, sofern diese noch nicht existieren.
    
    Diese Funktion prüft für jedes Fach in der Liste, ob es bereits in der Datenbank vorhanden ist, und legt es gegebenenfalls neu an.
    """
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
