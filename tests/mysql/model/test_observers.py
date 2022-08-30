import datetime
import json
import os
import unittest

import pendulum

from src.masoniteorm.collection import Collection
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, has_many, has_one
from src.masoniteorm.query.grammars import MSSQLGrammar
from tests.User import User

class Backup(Model):
    __table__ = 'backups'
    __guarded__ = []

    @classmethod
    def _boot(cls):
        cls.add_global_scope(lambda query: query.order_by('created_at', 'desc'))

        super(Backup, cls)._boot()

    @has_many('id', 'backup_id')
    def restores(self):
        return Restore

    @has_one('fallback_backup_id', 'id')
    def restore(self):
        return Restore


class Restore(Model):

    __appends__ = [
        'fallback_backup_id',
        'backup_id'
    ]

    @belongs_to('backup_id', 'id')
    def backup(self):
        return Backup

    @has_one('id', 'fallback_backup_id')
    def fallback(self):
        return Backup

    def createFallback(self):
        backup = Backup.create({
            'name': 'Backup before restore',
            'status': 'created',
        })
        self.attach('fallback', backup)
        self.save()


class RestoreObserver(object):
    def creating(self, restore):
        restore.backup.status = 'restoring'
        restore.backup.save()

    def created(self, restore):
        restore.createFallback()


Restore.observe(RestoreObserver())


class TestObserver(unittest.TestCase):
    def test_create_observer(self):
        backup_name = 'my_backup'
        backup_status = 'creating'
        backup = Backup.create(dict(
            name=backup_name,
            status=backup_status,
        ))
        restore = Restore.create(dict(
            backup_id=backup.id,
            fallback_backup_id=None,
        ))
        
        self.assertEqual(backup.name, backup_name)
        self.assertEqual(backup.status, backup_status)
        self.assertEqual(restore.backup_id, backup.id)

        self.assertEqual(Backup.count(), 2)
        self.assertEqual(Restore.count(), 1)
