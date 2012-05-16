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
        data = self.on_save({},instance)
        
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
        
        
    def on_load(self,data,model):
        """
        Called to sync the local model to the remote data.  Subclasses should override this method.
        """
        if hasattr(self.fields):
            for field in self.fields:
                try:
                    setattr(model,field,data[field])
                except AttributeError, KeyError:
                    log.warn(u'Cannot save field %s on model %s.  Field is either missing from Axilent content or local model.' % (field,unicode(model)))
            model.save()
        else:
            log.warn('Calling default on_load() method on ContentMapping for %s, but no fields have been defined.  No-op.' % unicode(self.model))
        
        return model
    
    def on_save(self,data,model):
        """
        Called to sync remote data to local model.  Subclasses should override this method.
        """
        if hasattr(self.fields):
            for field in self.fields:
                try:
                    data[field] = getattr(model,field)
                except AttributeError:
                    log.error('Local model %s does not have field %s, defined in the content binding.' % (unicode(self.model),field))
        else:
            log.warn('Calling default on_save() method on ContentMapping for %s, but no fields have been defined.  No-op.' % unicode(self.model))
        
        return data
    
    @property
    def saveable(self):
        """
        Indicates if the local models should be saved back to Axilent.  Defaults to True
        """
        if hasattr(self,'save_to_axilent'):
            return self.save_to_axilent
        else:
            return True
    
    @property
    def loadable(self):
        """
        Indicates if the local models should load data from Axilent.  Defaults to True.
        """
        if hasattr(self,'load_from_axilent'):
            return self.load_from_axilent
        else:
            return True

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
    
    def _build_kwargs(self,user,base_model):
        """
        Prepares keyword args for call.
        """
        kwargs = {}
        profile = self._get_profile(user)
        if profile:
            kwargs['profile'] = profile
        basekey = self._get_basekey(base_model)
        if basekey:
            kwargs['basekey'] = basekey
        return kwargs
        
    
    def get(self,user=None,limit=0,base_model=None):
        """
        Gets the Channel results as dictionaries.
        """
        try:
            kwargs = self._build_kwargs(user,base_model)
            kwargs['channel'] = self.slug
            print 'using kwargs',kwargs
            return self.client.contentchannel(**kwargs)
        except:
            log.exception('Exception while contacting Axilent.')
            return {}
    
    def get_models(self,user=None,limit=0,base_model=None):
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
                content_key = result['content']['key']
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
            kwargs = self._build_kwargs(user,base_model)
            kwargs['content_swap_slug'] = self.slug
            return self.client.policyswap(**kwargs)
        except:
            log.exception('Exception while contacting Axilent.')
            return {}
