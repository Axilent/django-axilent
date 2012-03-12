from axl.hooks import ContentMapping
from axl_example.models import Article

class ArticleMapping(ContentMapping):
    """
    Binds the Article model.
    """
    model = Article
    content_type = 'Article'
    pk_field = 'id' # this is actually the default - refers to the axilent content field that points to the model's primary key
    
    fields = ['name','body','section','published_on']
