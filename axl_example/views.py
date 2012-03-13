"""
Views for Axilent Example.
"""
from axilent.hooks import ContentChannel, ContentGroup
from axl_example.models import Article
from django.shortcuts import render_to_response

channel = ContentChannel('Django-Axilent Example Channel 1')
group = ContentGroup('Django-Axilent Example Group')

def index(request):
    """
    Main index page.  Pulls from a content channel, supplying a random basekey.
    """
    random_article = Article.objects.all().order_by('?')[0]
    results = group.get_models(user=request.user,base_model=random_article)
    return render_to_response('axl_example/index.html',{'results':results})

def article(request,article_id):
    """
    An article page.
    """
    article = Article.objects.get(pk=article_id)
    results = channel.get_models(user=request.user,base_model=article)
    return render_to_response('axl_example/article.html',{'article':article,'results':results})


