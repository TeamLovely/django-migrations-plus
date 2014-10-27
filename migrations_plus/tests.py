from django.db import connection
from django.db import router, DEFAULT_DB_ALIAS
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor
from django.db.migrations.migration import Migration
from django.db.migrations.state import ProjectState
from django.test import TestCase
from unittest.mock import patch

import migrations_plus


class TestRouter(object):
    # A test router. The behavior is vaguely primary/replica, but the
    # databases aren't assumed to propagate changes.

    def __init__(self):
        super().__init__()

    def db_for_read(self, model, instance=None, **hints):
        if instance:
            return instance._state.db or 'other'
        return 'other'

    def db_for_write(self, model, **hints):
        return DEFAULT_DB_ALIAS

    def allow_relation(self, obj1, obj2, **hints):
        return obj1._state.db in ('default', 'other') and obj2._state.db in ('default', 'other')

    def allow_migrate(self, db, model):
        return True


class TestRunSQL(TestCase):
    multi_db = True

    def setUp(self):
        self.old_routers = router.routers
        router.routers = [TestRouter()]

    def tearDown(self):
        router.routers = self.old_routers

    def apply_operations(self, app_label, project_state, operations):
        migration = Migration('name', app_label)
        migration.operations = operations
        with connection.schema_editor() as editor:
            return migration.apply(project_state, editor)

    def set_up_test_model(self, app_label):
        return self.apply_operations(app_label, ProjectState(), [])

    def test_default_database(self):
        """
        Tests the RunSQL operation with 'default' database
        """
        statement = 'SELECT 1;'
        project_state = self.set_up_test_model('test_app')
        operation = migrations_plus.RunSQL(statement)
        new_state = project_state.clone()
        operation.state_forwards('test_app', new_state)

        with connection.schema_editor() as editor:
            with patch.object(DatabaseSchemaEditor, 'execute') as patch_schema_editor:
                operation.database_forwards('test_app', editor, project_state, new_state)
                patch_schema_editor.assert_called_once_with(statement)

    def test_other_database(self):
        """
        Tests the RunSQL operation with 'other' database
        """
        statement = 'SELECT 1;'
        project_state = self.set_up_test_model('test_app')
        operation = migrations_plus.RunSQL(statement, db='other')
        new_state = project_state.clone()
        operation.state_forwards('test_app', new_state)

        with connection.schema_editor() as editor:
            with patch.object(DatabaseSchemaEditor, 'execute') as patch_schema_editor:
                editor.connection.alias = 'other'
                operation.database_forwards('test_app', editor, project_state, new_state)
                patch_schema_editor.assert_called_once_with(statement)
                editor.connection.alias = 'default'

    def test_database_not_called(self):
        """
        Tests the RunSQL operation checking that the wrong DB is not called
        """
        statement = 'SELECT 1;'

        project_state = self.set_up_test_model('test_app')
        operation = migrations_plus.RunSQL(statement, db='other')
        new_state = project_state.clone()
        operation.state_forwards('test_app', new_state)

        with connection.schema_editor() as editor:
            with patch.object(DatabaseSchemaEditor, 'execute') as patch_schema_editor:
                operation.database_forwards('test_app', editor, project_state, new_state)
                assert not patch_schema_editor.called

        project_state = self.set_up_test_model('test_app')
        operation = migrations_plus.RunSQL(statement)
        new_state = project_state.clone()
        operation.state_forwards('test_app', new_state)

        with connection.schema_editor() as editor:
            with patch.object(DatabaseSchemaEditor, 'execute') as patch_schema_editor:
                editor.connection.alias = 'other'
                operation.database_forwards('test_app', editor, project_state, new_state)
                assert not patch_schema_editor.called
                editor.connection.alias = 'default'
