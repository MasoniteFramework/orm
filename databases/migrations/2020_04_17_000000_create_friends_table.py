from src.masoniteorm.migrations.Migration import Migration

class CreateFriendsTable(Migration):

    def up(self):  
        """
        Run the migrations.
        """

        with self.schema.create('friends') as table:
            table.increments('id')
            table.string('name')
            table.integer('age')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('friends')