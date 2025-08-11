import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    """
    Gibt das SQLAlchemy-Engine-Objekt der aktuellen Flask-Anwendung zurück.
    
    Unterstützt sowohl Flask-SQLAlchemy-Versionen vor als auch ab Version 3, indem die jeweils passende Methode zur Engine-Ermittlung verwendet wird.
    """
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    """
    Gibt die Datenbank-URL der aktuellen SQLAlchemy-Engine als String zurück, wobei das Passwort sichtbar bleibt und Prozentzeichen für Alembic korrekt maskiert werden.
    
    Gibt:
        str: Die Datenbank-URL mit sichtbarem Passwort und doppelten Prozentzeichen.
    """
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    """
    Gibt das SQLAlchemy-MetaData-Objekt für die Migrationserstellung zurück.
    
    Wenn das Ziel-Datenbankobjekt mehrere Metadaten verwaltet, wird das Standard-MetaData-Objekt (`metadatas[None]`) zurückgegeben, andernfalls das einzelne `metadata`-Attribut.
    """
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """
    Führt Datenbankmigrationen im 'Offline'-Modus aus, indem Migrationen ohne aktive Datenbankverbindung generiert werden.
    
    Im Offline-Modus wird Alembic mit der Datenbank-URL und dem SQLAlchemy-Metadata-Objekt konfiguriert. SQL-Literale werden direkt in die generierten Migrationsskripte eingebettet.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Führt Datenbankmigrationen im 'Online'-Modus mit einer aktiven Datenbankverbindung durch.
    
    Konfiguriert Alembic mit einer bestehenden Verbindung und dem aktuellen SQLAlchemy-Metadata-Objekt. Unterdrückt die Generierung leerer Migrationsskripte, wenn keine Schemaänderungen erkannt werden.
    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        """
        Verhindert die Erstellung leerer Migrationsskripte bei der Autogenerierung.
        
        Wenn während der Autogenerierung keine Änderungen am Datenbankschema erkannt werden, werden die Migrationsdirektiven entfernt und ein Hinweis im Log ausgegeben.
        """
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
