"""kfupm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include 
from django.contrib.staticfiles.urls import static
from kfupm.settings import dev
import debug_toolbar
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.base import TemplateView 

from strawberry.django.views import GraphQLView
from .schema import schema


urlpatterns = [
    path('', include('account.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('evaluation/', include('evaluation.urls')),
    path('roommate/', include('roommate.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('endpoint/', csrf_exempt(GraphQLView.as_view(graphiql=False, schema=schema))),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]