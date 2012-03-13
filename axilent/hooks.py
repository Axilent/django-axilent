"""
Hooks for integration.
"""
from django.template.defaultfilters import slugify
import logging
from axilent.models import ContentBinding, AxilentProfile
from axilent import utils

log = logging.getLogger('django-axilent')

# ==================================
# = Django model / Axilent Content =
# ==================================

class ContentMapping(object):
    """
    Maps a Django model with an Axilent content type.
    """
    def save_to_axilent(self,instance):
        """
        Saves the instance to the appropriate Axilent content type.
        """
        # sanity check
        if not utils.project:
            raise Exception('You must define AXILENT_PROJECT in order to use content mappings.')
        
        binding = None
        app_label = instance._meta.app_label
        model_name = instance.__name__
        client = utils.resource('axilent.airtower','content')
        
        # populate field data
        data = {}
        for field in self.fields:
            data[field] = getattr(instance,field)
        
        try:
            binding = ContentBinding.objects.for_model(instance)
            # this is an update to existing content
            client.put(data={'project':project,
                             'content_type':self.content_type,
                             'key':binding.axilent_content_key,
                             'content':data})
            
        except ContentBinding.DoesNotExist:
            # No binding, content is being inserted into Axilent for the first time
            response = client.post(data={'project':project,
                                         'content_type':self.content_type,
                                         'content':data})
            response_content_type, response_content_key = response['created_content'].split(':')
            ContentBinding.objects.create_for_model(instance,response_content_type,response_content_key)
    
    def get_model(self,data):
        """
        Gets the local model for the supplied content result.
        """
        pk_field = 'id'
        if hasattr(self,'pk_field'):
            pk_field = self.pk_field
        
        try:
            model_pk = data[pk_field]
            return self.model.objects.get(pk=model_pk)
        except KeyError:
            raise Exception('The primary key field "%s" does not exist in the supplied content data.  Make sure the field has been defined visible in the Axilent content type.' % pk_field)
        

# ============
# = Triggers =
# ============
def trigger(category,action,user,**vars):
    """
    Triggers Axilent.
    """
    profile = AxilentProfile.objects.profile(user)
    client = utils.client('axilent.triggers')
    client.trigger(data={'profile':profile.profile,
                         'category':category,
                         'action':action,
                         'variables':vars})

# ====================
# = Content Channels =
# ====================
class ContentChannel(object):
    """
    Content channel.
    """
    def __init__(self,channel_name):
        """
        Constructor.
        """
        self.slug = slugify(channel_name)
        self.client = utils.client('axilent.content')
    
    def _get_profile(self,user=None):
        """
        Gets the profile for the specified user, if it exists.
        """
        profile = None
        if user and not user.is_anonymous():
            return AxilentProfile.objects.profile(user).profile
        else:
            return None
    
    def _get_basekey(self,base_model=None):
        """
        Gets the basekey for the specified model, if it exists.
        """
        if base_model:
            try:
                return ContentBinding.objects.for_model(base_model).axilent_content_key
            except ContentBinding.DoesNotExist:
                return None
    
    def get(self,user=None,limit=None,base_model=None):
        """
        Gets the Channel results as dictionaries.
        """
        try:
            return self.client.policycontent(profile=self._get_profile(user),content_policy_slug=self.slug,basekey=self._get_basekey(base_model))
        except:
            log.exception('Exception while contacting Axilent.')
            return {}
    
    def get_models(self,user=None,limit=None,base_model=None):
        """
        Gets the Channel results, reconstituted as models.
        """
        model_results = {}
        raw_results = self.get(user=user,limit=limit,base_model=base_model)
        for group_name in raw_results.keys():
            group_model_results = []
            group_results = raw_results[group_name]
            for result in group_results:
                content_type = result['content']['content_type']
                content_key = int(result['content']['key'])
                try:
                    binding = ContentBinding.objects.get(axilent_content_type=content_type,axilent_content_key=content_key)
                    group_model_results.append(binding.get_model())
                except ContentBinding.DoesNotExist:
                    log.exception('No content binding for %s:%s found in local database.' % (content_type,content_key))
            model_results[group_name] = group_model_results
        
        return model_results

class ContentGroup(ContentChannel):
    """
    Very similar to a content channel, but addresses a content group ('policyswap') instead.
    """
    def get(self,user=None,limit=None,base_model=None):
        """
        Addresses the group.
        """
        try:
            return self.client.policyswap(profile=self._get_profile(user),content_swap_slug=self.slug,basekey=self._get_basekey(base_model))
        except:
            log.exception('Exception while contacting Axilent.')
            return {}
