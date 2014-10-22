from django.db import migrations


class RunSQL(migrations.RunSQL):

    def __init__(self, sql, reverse_sql=None, state_operations=None, db='default'):
        self.db = db
        self.sql = sql
        self.reverse_sql = reverse_sql
        self.state_operations = state_operations or []

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.alias != self.db:
            return

        statements = schema_editor.connection.ops.prepare_sql_script(self.sql)
        for statement in statements:
            schema_editor.execute(statement)
