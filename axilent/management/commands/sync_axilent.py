"""
Loads content from Axilent, syncing local models according to thier content mappings.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    """
    Command class.
    """
    def handle(self,*args,**kwargs):
        """
        Handler method.
        """
        if len(args):
            self.sync_app(args[0])
        else:
            # sync all the apps
            for app_path in settings.INSTALLED_APPS:
                if app_path != 'axilent': # don't sync yourself
                    self.sync_app(app_path)
            
    def sync_app(self,app_name):
        """
        Synchronizes an app.
        """
        print 'synchonizing',app_name,'to Axilent.'
        
    