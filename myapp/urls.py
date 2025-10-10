from django.contrib import admin
from django.urls import path, include  
from diary import views as diary_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('diary/', include('diary.urls')), 
    path('home', diary_views.calendar_view, name='home'),
    path('calendar/', diary_views.calendar_view, name='calendar'),
    path('login/', diary_views.login_view, name='login'),
    path("logout/", diary_views.logout_view, name="logout"),
    path("signup/", diary_views.signup_view, name="signup"),
    path('', diary_views.portfolio, name='portfolio'),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)