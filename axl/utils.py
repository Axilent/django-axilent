"""
Utilities for the Axl package.
"""
# ============
# = Settings =
# ============
end_point = 'https://www.axilent.net'
api_key = None
api_version = 'beta1'
api_path = '/api'
resource_path = '/api/resource'
project = None

from django.conf import settings

if hasattr(settings,'AXILENT_ENDPOINT') and settings.AXILENT_ENDPOINT:
    end_point = settings.AXILENT_ENDPOINT

if hasattr(settings,'AXILENT_API_KEY') and settings.AXILENT_API_KEY:
    api_key = settings.AXILENT_API_KEY

if hasattr(settings,'AXILENT_API_VERSION') and settings.AXILENT_API_VERSION:
    api_version = settings.AXILENT_API_VERSION

if hasattr(settings,'AXILENT_FUNCTION_PATH') and settings.AXILENT_FUNCTION_PATH:
    api_path = settings.AXILENT_FUNCTION_PATH

if hasattr(settings,'AXILENT_RESOURCE_PATH') and settings.AXILENT_RESOURCE_PATH:
    resource_path = settings.AXILENT_RESOURCE_PATH

if hasattr(settings,'AXILENT_PROJECT') and settings.AXILENT_PROJECT:
    project = settings.AXILENT_PROJECT

# sanity check
if not api_key:
    raise Exception('You must set the AXILENT_APIKEY to use Django-Axilent.')

# =====================
# = Utility Functions =
# =====================
from sharrock.client import HttpClient, ResourceClient

def client(axilent_app):
    """
    Gets a basic http client.
    """
    return HttpClient('%s%s' % (end_point,api_path),axilent_app,api_version,auth_user=api_key)

def resource(axilent_app,resource):
    """
    Gets a resource client.
    """
    return ResourceClient('%s%s' % (end_point,resource_path),axilent_app,api_version,resource,auth_user=api_key)

def get_model_instance(app_label,model_name,pk):
    """
    Gets the instance of the model signified by the supplied app label, model class name and primary key.
    """
    # 1. get the appropriate parent module for the app
    module = __import__(app_label)
    components = app_label.split('.')
    for comp in components[1:]:
        module = getattr(module,comp)
    
    # 2. Get models
    models = getattr(module,'models')
    
    # 3. Get the specified model class
    model_class = getattr(models,model_name)
    
    # 4. Get the instance
    return model_class.objects.get(pk=pk)


