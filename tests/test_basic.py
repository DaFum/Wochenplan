import unittest

from app import create_app, db


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        """
        Initialisiert die Testumgebung für jeden Testfall, einschließlich einer Flask-App im Testmodus, einer In-Memory-Datenbank und eines Testclients.
        """
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
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


if __name__ == '__main__':
    unittest.main()
