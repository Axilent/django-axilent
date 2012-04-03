"""
Loads content from Axilent, syncing local models according to thier content mappings.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from axilent.registry import get_content_mappings
from axilent import utils
from axilent.models import ContentBinding
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    """
    Command class.
    """
    resource = utils.resource('axilent.content','content')
    client = utils.client('axilent.content')
    
    def handle(self,*args,**kwargs):
        """
        Handler method.
        """
        if len(args):
            self.sync_app(args[0])
        else:
            # sync all the apps
            for app_path in settings.INSTALLED_APPS:
                if app_path != 'axilent' and not app_path.startswith('django'): # don't sync yourself or django contrib apps
                    self.sync_app(app_path)
            
    def sync_app(self,app_name):
        """
        Synchronizes an app.
        """
        print 'synchonizing',app_name,'to Axilent.'
        for content_mapping in get_content_mappings(app_name):
            if content_mapping.loadable:
                keys = client.getcontentkeys(content_type_slug=slugify(content_mapping.content_type))
                for content_key in keys:
                    data = resource.get(content_type_slug=slugify(content_mapping.content_type),
                                        content_key=content_key)
                    try:
                        binding = ContentBinding.objects.get(axilent_content_type=content_mapping.content_type,
                                                             axilent_content_key=content_key)
                        content_mapping.on_load(data,binding.get_model()) # Update existing model
                        print 'Updated locally cached model',binding.get_model(),'with',content_mapping.content_type,':',content_key
                    except ContentBinding.DoesNotExist:
                        # First time data has been cached locally
                        model = content_mapping.on_load(data,content_mapping.model()) # Instantiate a new model and load it from the data
                        ContentBinding.objects.create_for_model(model,content_mapping.content_type,content_key) # create binding for new model
                        print 'Caching',model,'from',content_mapping.content_type,':',content_key,'for the first time.'
