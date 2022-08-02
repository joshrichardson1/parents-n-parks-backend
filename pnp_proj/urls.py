
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pnp_app.urls')),
    path('friends/', include('friend_app.urls')),
]
