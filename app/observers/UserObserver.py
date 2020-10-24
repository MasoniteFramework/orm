"""User Observer"""

from masoniteorm.models import Model


class UserObserver:
    def created(self, clients):
        """Handle the Clients "created" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def creating(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def saving(self, clients):
        """Handle the Clients "saving" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def saved(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def updating(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def updated(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def booted(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def booting(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def hydrating(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def hydrated(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def deleting(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass

    def deleted(self, clients):
        """Handle the Clients "creating" event.

        Args:
            clients (masoniteorm.models.Model): Clients model.
        """
        pass
