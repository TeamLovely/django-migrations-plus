django-migrations-plus
======================

Migrations Plus provides a method to run raw SQL in Django migrations with multiple DB connections.

Install
-------

Using pip::
    
    $ pip install django-migrations-plus

API
-----
``RunSQL(sql, reverse_sql=None, state_operations=None, db='default')``

Allows running of arbitrary SQL on the database - useful for more advanced features of database backends that Django doesn’t support directly, like partial indexes.

sql, and reverse_sql if provided, should be strings of SQL to run on the database. On most database backends (all but PostgreSQL), Django will split the SQL into individual statements prior to executing them. This requires installing the sqlparse Python library.

The state_operations argument is so you can supply operations that are equivalent to the SQL in terms of project state; for example, if you are manually creating a column, you should pass in a list containing an AddField operation here so that the autodetector still has an up-to-date state of the model (otherwise, when you next run makemigrations, it won’t see any operation that adds that field and so will try to run it again).

db should be a string with the name of the connection from your settings you want to run your SQL on.

Example
-------
.. code-block:: python

    from django.db import migrations
    import migrations_plus


    class Migration(migrations.Migration):

        operations = [
            migrations_plus.RunSQL('DROP TABLE Students;')  # Runs only against connection 'default'
            migrations_plus.RunSQL('DROP TABLE OtherStudents;', db='other')  # Runs only against connection 'other'
        ]
