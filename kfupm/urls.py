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
from graphene_django.views import GraphQLView


urlpatterns = [
    path('', include('account.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('evaluation/', include('evaluation.urls')),
    path('roommate/', include('roommate.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('maintenance-mode/', include('maintenance_mode.urls')),
    path('ingredients/', include('ingredients.urls')),
    path('graphql/', GraphQLView.as_view(graphiql=True)),


]
# WARNING: this setting is only for development environment
urlpatterns += static(dev.MEDIA_URL, document_root=dev.MEDIA_ROOT)