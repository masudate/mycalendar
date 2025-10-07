from django.contrib import admin
from django.urls import path, include  
from diary import views as diary_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('diary/', include('diary.urls')), 
    path('', diary_views.calendar_view, name='home'),
    path('login/', diary_views.login_view, name='login'),
    path("logout/", diary_views.logout_view, name="logout"),
    path("signup/", diary_views.signup_view, name="signup"),
    path('portfolio/', diary_views.portfolio, name='portfolio'),
]


if settings.DEBUG:
    # /static 用：staticfiles のファインダー経由（STATICFILES_DIRS を含めて解決）
    urlpatterns += staticfiles_urlpatterns()

    # /media 用：MEDIA_ROOT を配信
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)