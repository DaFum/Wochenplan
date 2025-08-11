import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db


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
            self.assertEqual(updated.status, 'COMPLETED')

    def test_delete_task(self):
        """Prüft, ob das Löschen einer Aufgabe funktioniert."""
        with self.app.app_context():
            task = self.app.task_manager.add_task('Loeschen')
            tid = task.id
        resp = self.client.post(f'/task/{tid}/delete')
        self.assertEqual(resp.status_code, 302)
        with self.app.app_context():
            self.assertIsNone(self.app.task_manager.get_task(tid))


if __name__ == '__main__':
    unittest.main()
