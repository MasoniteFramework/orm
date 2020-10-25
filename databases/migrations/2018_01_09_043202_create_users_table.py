from src.masoniteorm.migrations import Migration
from tests.User import User


class CreateUsersTable(Migration):

    def up(self):
        """Run the migrations."""
        with self.schema.create('users') as table:
            table.increments('id')
            table.string('name')
            table.string('email').unique()
            table.string('password')
            table.string('second_password').nullable()
            table.string('remember_token').nullable()
            table.timestamp('verified_at').nullable()
            table.timestamps()

        if not self.schema._dry:
            User.on(self.connection).create({
                'name': 'Joe',
                'email': 'joe@email.com',
                'password': 'secret'
            })

    def down(self):
        """Revert the migrations."""
        self.schema.drop('users')
