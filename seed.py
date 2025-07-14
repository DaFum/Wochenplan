from app import create_app, db
from app.models import Subject

def seed_subjects():
    app = create_app()
    with app.app_context():
        if Subject.query.count() == 0:
            default_subjects = [
                'Mathematik', 'Deutsch', 'Englisch', 'Biologie',
                'Chemie', 'Physik', 'Geschichte', 'Geographie',
                'Sport', 'Kunst', 'Musik'
            ]
            for subject_name in default_subjects:
                subject = Subject(name=subject_name)
                db.session.add(subject)
            db.session.commit()
            print('Default subjects have been seeded.')
        else:
            print('Subjects table is not empty. Skipping seeding.')

if __name__ == '__main__':
    seed_subjects()
