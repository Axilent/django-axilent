"""
Example models file.
"""
from django.db import models

class Author(models.Model):
    """
    An author.  Example model.
    """
    first_name = models.CharField(blank=True, max_length=100)
    last_name = models.CharField(blank=True, max_length=100)
    
class Article(models.Model):
    """
    An example model.
    """
    name = models.CharField(blank=True, max_length=100)
    body = models.TextField(blank=True)
    author = models.ForeignKey(Author,related_name='articles')
    section = models.CharField(blank=True, max_length=100)
    published_on = models.DateField()
    
    def __unicode__(self):
        return self.name

