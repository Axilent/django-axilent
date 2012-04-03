"""
Main registry for Axilent objects in the Django app.
"""
from django.conf import settings
from sharrock.registry import get_module
import inspect
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

log = logging.getLogger('axilent.registry')

content_mappings = {}
reverse_content_mappings = {}

def register_apps():
    """
    Main registration method.
    """
    for app_path in settings.INSTALLED_APPS:
        if app_path != 'axilent': # don't load yourself
            try:
                channel_module = get_module('%s.axl.channels' % app_path)
                load_channels(app_path,channel_module)
            except ImportError:
                pass # no channels defined
            
            try:
                trigger_module = get_module('%s.axl.triggers' % app_path)
                load_triggers(app_path,trigger_module)
            except ImportError:
                pass # no triggers defined
            
            try:
                content_module = get_module('%s.axl.content' % app_path)
                load_content(app_path,content_module)
            except ImportError:
                pass # no content mappings defined

def load_channels(app_path,module):
    """
    Loads channel mapping from the specified module.
    """
    pass # TODO

def load_triggers(app_path,module):
    """
    Loads trigger mappings from the specified module.
    """
    pass # TODO 

def load_content(app_path,module):
    """
    Loads content mappings from the specified module.
    """
    from axl.hooks import ContentMapping
    for name,attribute in inspect.getmembers(module):
        if inspect.isclass(attribute) and issubclass(attribute,ContentMapping) and not attribute is ContentMapping:
             content_mappings[attribute.model] = attribute() # put an instance of the ContentMapping keyed to its Model class
             reverse_content_mappings[attribute.content_type] = attribute() # put in instance in a map keyed to the content type name
             log.info('Registered Axilent content mapping for model %s.' % unicode(attribute.model))

# ================
# = Signal hooks =
# ================

@receiver(post_save)
def on_content_save(sender,**kwargs):
    """
    Receiver function for model saves - will update bound Axilent content.
    """
    try:
        mapping = content_mappings[sender]
        if mapping.saveable:
            mapping.save_to_axilent(kwargs['instance'])
    except KeyError:
        pass # no mapping for that model

    