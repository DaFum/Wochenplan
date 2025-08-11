import os
import sys
import unittest
from datetime import datetime
from urllib.parse import quote

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import TaskPriority, TaskStatus
from werkzeug.utils import secure_filename
from unittest.mock import patch
from PIL import Image as PILImage


def _fake_image(*args, **kwargs):
    img = PILImage.new('RGB', (1, 1))
    if kwargs.get('save') and kwargs.get('file'):
        img.save(kwargs['file'])
    return img


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        """
        Initialisiert die Testumgebung für jeden Testfall, einschließlich einer Flask-App im Testmodus, einer In-Memory-Datenbank und eines Testclients.
        """
        os.environ['SECRET_KEY'] = 'test-secret'
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Bereinigt die Testumgebung, indem die Datenbanksitzung entfernt und alle Tabellen nach jedem Test gelöscht werden.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_main_page(self):
        """
        Testet, ob die Hauptseite der Anwendung erfolgreich geladen wird und einen HTTP-Statuscode 200 zurückgibt.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_reorder_task(self):
        """Tests if task reordering functionality works."""
        with self.app.app_context():
            t1 = self.app.task_manager.add_task('A')
            t2 = self.app.task_manager.add_task('B')
            t1_id, t2_id = t1.id, t2.id
        resp = self.client.post(f'/task/{t1_id}/reorder', json={'position': 1})
        self.assertEqual(resp.status_code, 200)
        with self.app.app_context():
            tasks = self.app.task_manager.list_tasks()
            self.assertEqual([t.id for t in tasks], [t2_id, t1_id])

    def test_edit_task(self):
        """Prüft, ob das Bearbeiten einer Aufgabe funktioniert."""
        with self.app.app_context():
            task = self.app.task_manager.add_task('Alt')
            tid = task.id
        resp = self.client.post(f'/task/{tid}/edit', data={'title': 'Neu'})
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            updated = self.app.task_manager.get_task(tid)
            self.assertEqual(updated.title, 'Neu')

    def test_change_status(self):
        """Prüft, ob das Ändern des Status einer Aufgabe funktioniert."""
        with self.app.app_context():
            task = self.app.task_manager.add_task('Status')
            tid = task.id
        resp = self.client.post(f'/task/{tid}/status', data={'status': 'COMPLETED'})
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            updated = self.app.task_manager.get_task(tid)
            self.assertEqual(updated.status, TaskStatus.COMPLETED)

    def test_delete_task(self):
        """Prüft, ob das Löschen einer Aufgabe funktioniert."""
        with self.app.app_context():
            task = self.app.task_manager.add_task('Loeschen')
            tid = task.id
        resp = self.client.post(f'/task/{tid}/delete')
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            deleted = self.app.task_manager.get_task(tid)
            self.assertIsNone(deleted)

    def test_ical_contains_uid_and_dtstamp(self):
        """Sicherstellt, dass iCal-Export UID und DTSTAMP enthält."""
        with self.app.app_context():
            task = self.app.task_manager.add_task('ICS')
            tid = task.id
        resp = self.client.get('/download-ical')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8')
        self.assertIn(f'UID:task-{tid}@wochenplan', data)
        self.assertIn('DTSTAMP', data)

    def test_task_due_date_and_priority(self):
        """Tasks speichern Fälligkeitsdatum und Priorität korrekt."""
        with self.app.app_context():
            due = datetime(2025, 1, 1, 12, 0)
            task = self.app.task_manager.add_task(
                'Mit Datum', priority=TaskPriority.HIGH, due_date=due
            )
            fetched = self.app.task_manager.get_task(task.id)
            self.assertEqual(fetched.priority, TaskPriority.HIGH)
            self.assertEqual(fetched.due_date, due)

    @patch('pollinations.image.Image.__call__', new=_fake_image)
    def test_subject_add_creates_image(self):
        """Beim Hinzufügen eines Faches wird ein statisches Bild gespeichert."""
        subject = 'Astrophysik'
        image_path = os.path.join(
            self.app.static_folder, 'subjects', secure_filename(subject) + '.png'
        )
        def cleanup_image(path):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except (OSError, IOError) as e:
                print(f"Warning: Failed to clean up test image at {path}: {e}")
        self.addCleanup(cleanup_image, image_path)

        resp = self.client.post(
            '/einstellungen', data={'new_subject': subject, 'submit': True}, follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(os.path.exists(image_path))

    def test_task_has_dynamic_image_url(self):
        """Aufgaben erhalten eine dynamische Pollinations-Bild-URL."""
        with self.app.app_context():
            self.app.task_manager.add_task('Hausaufgabe')
        resp = self.client.get('/')
        expected = f"image.pollinations.ai/prompt/{quote('Hausaufgabe')}"
        self.assertIn(expected, resp.get_data(as_text=True))
    def test_library_tasks_endpoint(self):
        """Content library tasks are exposed via API."""
        resp = self.client.get('/api/library-tasks/Mathematik')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('Hausaufgaben erledigen', data.get('tasks', []))


if __name__ == '__main__':
    unittest.main()
