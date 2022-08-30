"""CreateBackupRestoreTable Migration."""

from masoniteorm.migrations import Migration


class CreateBackupRestoreTable(Migration):
    
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('backups') as table:
            table.big_increments('id')
            table.string('name', 191)
            table.enum('status', ['creating','created','deleting','restoring','restored']).default('creating')
            table.timestamps()
        
        with self.schema.create('restores') as table:
            table.increments('id')
            table.big_integer('backup_id').unsigned()
            table.big_integer('fallback_backup_id').unsigned().nullable().default(None)
            table.timestamps()

            table.unique('fallback_backup_id', name='restores_fallback_backup_id_unique')
            table.index('backup_id', name='restores_backup_id_index')
            table.foreign('backup_id', name='restores_backup_id_foreign') \
                .references('id').on('backups') \
                .on_delete('cascade')
            table.foreign('fallback_backup_id', name='restores_fallback_backup_id_foreign') \
                .references('id').on('backups') \
                .on_delete('set null')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('backups')

        self.schema.drop('restores')
