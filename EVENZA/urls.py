"""
URL configuration for EVENZA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

# urls.py
from django.urls import path
from EVENZA import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ==================== PUBLIC URLS ====================
    path('admin/', admin.site.urls),  
    path('', views.fun, name='funn'),
    path('home', views.home, name='home'),
    path('core/index/', views.index, name='indexx'),
    path('b_events/', views.b_events, name='b_events'),
    path('a_events/', views.a_events, name='a_events'),
    path('core/gallery/', views.gallery, name='gallery'),
    path('core/about/', views.about, name='about'),
    path('core/contact/', views.contact, name='contact'),
    path('user/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==================== STUDENT URLS ====================
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # ==================== ADMIN URLS ====================
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Event management
    path('add_event/', views.add_event, name='add_event'),
    path('edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('view_event/<int:event_id>/', views.view_event, name='view_event'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    
    # Student management
    path('add_student/', views.add_student, name='add_student'),
    path('edit_student/<int:student_name>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_name>/', views.delete_student, name='delete_student'),
    
    # Announcement management
    path('add_announcement/', views.add_announcement, name='add_announcement'),
    path('edit_announcement/<int:announcement_id>/', views.edit_announcement, name='edit_announcement'),
    path('delete_announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    
    # Participation management
    path('student_participation/<int:student_id>/', views.student_participation, name='student_participation'),
    path('mark_attendance/<int:event_id>/', views.mark_attendance, name='mark_attendance'),
    path('events/', views.event_list, name='event_list'),
    path('register_event/<int:event_id>/', views.register_event, name='register_event'),
    path('event_participants/<int:event_id>/', views.event_participants, name='event_participants'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

