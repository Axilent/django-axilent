"""
Models for Django-Axilent.  Mostly just used as a hook to set up structure.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid
from axl.utils import get_model_instance

class AxilentProfileManager(models.Manager):
    """
    Manager class for Axilent profiles.
    """
    def profile(self,user):
        """
        Gets or creates an axilent profile for the user.
        """
        try:
            return self.get(user=user)
        except AxilentProfile.DoesNotExist:
            return self.create(user=user,profile=uuid.uuid4().hex)
    
class AxilentProfile(models.Model):
    """
    Binds a user with an axilent profile.
    """
    user = models.ForeignKey(User,unique=True)
    profile = models.CharField(max_length=100,unique=True)
    
    objects = AxilentProfileManager()
    
    def __unicode__(self):
        return '%s:%s' % (unicode(self.user),self.profile)

class ContentBindingManager(models.Manager):
    """
    Manager class for content bindings.
    """
    def for_model(self,instance):
        """
        Gets the content binding for the model, if it exists.
        """
        app_label = instance._meta.app_label
        model_name = instance.__name__
        return self.get(app_label=app_label,model_name=model_name,model_pk=instance.pk)
    
    def create_for_model(self,instance,axilent_content_type,axilent_content_key):
        """
        Creates a binding.
        """
        app_label = instance._meta.app_label
        model_name = instance.__name__
        return self.create(app_label=app_label,
                           model_name=model_name,
                           model_pk=instance.pk,
                           axilent_content_type=axilent_content_type,
                           axilent_content_key=axilent_content_key)
        
    
class ContentBinding(models.Model):
    """
    Binds an instance of a model with a specific Axilent content mapping.
    """
    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    model_pk = models.IntegerField()
    axilent_content_type = models.CharField(max_length=100)
    axilent_content_key = models.CharField(max_length=100)
    
    objects = ContentBindingManager()
    
    def __unicode__(self):
        return u'%s.%s:%d::%s:%s' % (self.app_label,self.model_name,self.model_pk,self.axilent_content_type,self.axilent_content_key)
    
    def get_model(self):
        """
        Gets the model instance represented by this binding.
        """
        return get_model_instance(self.app_label,self.model_name,self.model_pk)
    
    class Meta:
        unique_together = (('app_label','model_name','model_pk'),('axilent_content_type','axilent_content_key'))

    
# =========================
# = Hook to register apps =
# =========================
from axl.registry import register_apps
register_apps()
