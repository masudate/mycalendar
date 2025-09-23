from django.urls import path
from . import views


urlpatterns = [
    path('', views.calendar_view, name='calendar'),  # カレンダー画面（ホーム）
    path('settings/', views.settings_view, name='settings'), #設定画面
    path('record/', views.record_view, name='record'), #記録する画面
    path('record/<str:selected_date>/', views.record_view, name='record_with_date'),
    path("records/<int:pk>/delete/", views.record_delete, name="record_delete"),
    path("records/<int:pk>/photo_delete/", views.photo_delete, name="photo_delete"),

    
    #設定関連
    path('settings/username/', views.change_username, name='change_username'),
    path('settings/email/', views.change_email, name='change_email'),
    path('settings/password/', views.change_password, name='change_password'),
]

