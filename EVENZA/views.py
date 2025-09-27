# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from mainapp.models import Student, Event, Participation, Announcement
from django.contrib import messages
import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from django.core.files.storage import FileSystemStorage

# Admin credentials (should be moved to settings.py in production)
ADMIN_CREDENTIALS = {
    'studentname': 'admin',
    'Enrollment': 'admin123'
}

# ==================== PUBLIC VIEWS ====================

def fun(request):
    """Redirect to appropriate page based on user session"""
    user = request.session.get('student_name') or request.session.get('admin_studentname')
    return redirect('indexx') if user else redirect('home')

def index(request):
    """Home page for logged-in users"""
    return render(request, 'core/index.html')

def home(request):
    """Public home page"""
    return render(request, 'core/home.html')

def gallery(request):
    """Gallery page"""
    return render(request, 'core/gallery.html')

def about(request):
    """About page"""
    return render(request, 'core/about.html')

def contact(request):
    """Contact page"""
    return render(request, 'core/contact.html')

def b_events(request):
    """Events page for non-authenticated users"""
    now = timezone.now()
    upcoming_events = Event.objects.filter(date__gte=now).order_by('date')[:3]
    all_events = Event.objects.all().order_by('-date')
    
    context = {
        'upcoming_events': upcoming_events,
        'all_events': all_events
    }
    return render(request, 'core/before_events.html', context)

def a_events(request):
    """Events page for authenticated users"""
    now = timezone.now()
    category = request.GET.get('category', 'upcoming')
    events = Event.objects.all().order_by('-date')
    
    if category == 'upcoming':
        events = events.filter(date__gte=now)
    elif category != 'all':
        events = events.filter(category=category)
    
    context = {
        'events': events,
        'active_category': category
    }
    return render(request, 'core/after_events.html', context)

# ==================== AUTHENTICATION ====================

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        studentname = request.POST.get('studentname')
        Enrollment = request.POST.get('Enrollment')
        
        # Check admin credentials
        if studentname == ADMIN_CREDENTIALS['studentname'] and Enrollment == ADMIN_CREDENTIALS['Enrollment']:
            request.session['user_type'] = 'admin'
            request.session['admin_studentname'] = ADMIN_CREDENTIALS['studentname']
            return redirect('admin_dashboard')
        
        # Check student credentials
        try:
            student = Student.objects.get(student_name=studentname, Enrollment=Enrollment, is_active=True)
            request.session['user_type'] = 'student'
            request.session['student_name'] = student.id
            return redirect('indexx')
        except Student.DoesNotExist:
            error = "Invalid credentials"
            return render(request, 'user/login.html', {'error': error})
    
    return render(request, 'user/login.html')

def logout_view(request):
    """Handle user logout"""
    request.session.flush()
    return redirect('home')

# ==================== ADMIN DASHBOARD ====================

def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    now = timezone.now()
    events = Event.objects.all().order_by('-date')
    students = Student.objects.all()
    announcements = Announcement.objects.filter(target__in=['all', 'admin']).order_by('-created_at')
    
    context = {
        'events': events,
        'students': students,
        'announcements': announcements,
        'upcoming_events_count': Event.objects.filter(date__gte=now).count(),
        'total_participants': Student.objects.count(),
        'pending_certificates': 0,  # Placeholder
        'new_announcements': Announcement.objects.filter(
            created_at__date=timezone.localdate(),
            target__in=['all', 'admin']
        ).count(),
        'studentname': request.session.get('admin_studentname', 'Admin')
    }
    return render(request, 'user/admin_dashboard.html', context)

# ==================== EVENT MANAGEMENT ====================

def add_event(request, event_id=None):
    """Add or edit an event"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id) if event_id else None
    
    if request.method == 'POST':
        # Create new event
        event = Event.objects.create(
            title=request.POST.get('title'),
            date=request.POST.get('date'),
            location=request.POST.get('location'),
            image=request.FILES.get('image'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
        )
        messages.success(request, 'Event created successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'events/event_form.html', {'event': event})

def edit_event(request, event_id):
    """Edit an existing event"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        # Update existing event
        event.title = request.POST.get('title')
        event.date = request.POST.get('date')
        event.location = request.POST.get('location')
        event.description = request.POST.get('description')
        event.category = request.POST.get('category')
        event.is_completed = request.POST.get('is_completed') == 'on'
        
        if request.FILES.get('image'):
            event.image = request.FILES.get('image')
        
        event.save()
        messages.success(request, 'Event updated successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'events/event_form.html', {'event': event})

def view_event(request, event_id):
    """View event details"""
    event = get_object_or_404(Event, id=event_id)
    
    # Admin view
    if request.session.get('user_type') == 'admin':
        participations = Participation.objects.filter(event=event).select_related('student')
        
        context = {
            'event': event,
            'participations': participations,
            'total_participants': participations.count(),
            'attended_count': participations.filter(attended=True).count()
        }
        return render(request, 'events/event_view.html', context)
    
    # Student view
    elif request.session.get('student_name'):
        student = get_object_or_404(Student, id=request.session['student_name'])
        
        try:
            participation = Participation.objects.get(student=student, event=event)
            registered, attended = True, participation.attended
        except Participation.DoesNotExist:
            registered, attended = False, False
        
        context = {
            'event': event,
            'registered': registered,
            'attended': attended
        }
        return render(request, 'events/event_view.html', context)
    
    # Unauthenticated users
    return redirect('login')

def delete_event(request, event_id):
    """Delete an event (AJAX)"""
    if not request.session.get('user_type') == 'admin':
        return JsonResponse({'status': 'unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    
    return JsonResponse({'status': 'invalid_method'}, status=400)

# ==================== STUDENT MANAGEMENT ====================

def add_student(request):
    """Add a new student"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    form_data = request.session.pop('form_data', {})
    error_message = request.session.pop('error_message', None)
    
    if request.method == 'POST':
        request.session['form_data'] = request.POST.dict()
        student_name = request.POST.get('student_name')
        Enrollment = request.POST.get('Enrollment')
        
        # Validation
        if not student_name or not Enrollment:
            request.session['error_message'] = "All fields are required!"
            return redirect('add_student')
        
        if Student.objects.filter(student_name=student_name).exists():
            request.session['error_message'] = f"Student Name {student_name} already exists!"
            return redirect('add_student')
        
        # Create student
        try:
            Student.objects.create(student_name=student_name, Enrollment=Enrollment)
            if 'form_data' in request.session:
                del request.session['form_data']
            return redirect(reverse('admin_dashboard') + '#manage-students')
        except Exception as e:
            request.session['error_message'] = f"Error: {str(e)}"
            return redirect('add_student')
    
    context = {'form_data': form_data, 'error_message': error_message}
    return render(request, 'events/student_form.html', context)

def edit_student(request, student_name):
    """Edit an existing student"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    student = get_object_or_404(Student, id=student_name)
    
    if request.method == 'POST':
        new_student_name = request.POST.get('student_name', student.student_name)
        name = request.POST.get('name', student.id)
        Enrollment = request.POST.get('Enrollment')
        
        # Validation
        if not new_student_name or not name:
            return HttpResponse(
                '<script>alert("Student ID and Name are required!");'
                f'window.location.href = "{reverse("edit_student", args=[student.id])}";</script>'
            )
        
        if new_student_name != student.student_name and Student.objects.filter(student_name=new_student_name).exists():
            return HttpResponse(
                f'<script>alert("Student ID {new_student_name} already exists!");'
                f'window.location.href = "{reverse("edit_student", args=[student.id])}";</script>'
            )
        
        # Update student
        student.student_name = new_student_name
        student.name = name
        if Enrollment:
            student.Enrollment = Enrollment
        
        try:
            student.save()
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(
                f'<script>alert("Error: {str(e)}");'
                f'window.location.href = "{reverse("edit_student", args=[student.id])}";</script>'
            )
    
    return render(request, 'events/student_form.html', {'student': student})

def student_participation(request, student_id):
    """View student participation history"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    student = get_object_or_404(Student, id=student_id)
    participations = Participation.objects.filter(student=student).select_related('event')
    
    # Categorize participations
    current_time = timezone.now()
    upcoming = [p for p in participations if p.attended or (p.event.date >= current_time and p.is_registered)]
    attended = [p for p in participations if p.attended]
    
    context = {
        'student': student,
        'upcoming_registrations': upcoming,
        'attended_events': attended
    }
    return render(request, 'events/student_participation.html', context)

def delete_student(request, student_name):
    """Delete a student (AJAX)"""
    if not request.session.get('user_type') == 'admin':
        return JsonResponse({'status': 'unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            student = Student.objects.get(id=student_name)
            student.delete()
            return JsonResponse({'status': 'success'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    
    return JsonResponse({'status': 'invalid_method'}, status=400)

# ==================== ANNOUNCEMENT MANAGEMENT ====================

def add_announcement(request):
    """Add or edit an announcement"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        created_at_str = request.POST.get('created_at')
        target = request.POST.get('target', 'all')
        announcement_id = request.POST.get('announcement_id')
        
        try:
            created_at = datetime.datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
            
            if announcement_id:
                announcement = Announcement.objects.get(id=announcement_id)
                announcement.title = title
                announcement.content = content
                announcement.created_at = created_at
                announcement.target = target
                announcement.save()
                messages.success(request, 'Announcement updated successfully!')
            else:
                Announcement.objects.create(
                    title=title,
                    content=content,
                    created_at=created_at,
                    target=target
                )
                messages.success(request, 'Announcement created successfully!')
            return redirect(reverse('admin_dashboard') + '#announcements')
        
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            context = {
                'title': title,
                'content': content,
                'created_at_str': created_at_str,
                'target': target,
            }
            if announcement_id:
                context['announcement_id'] = announcement_id
            return render(request, 'events/announcement_form.html', context)
    
    default_created_at = timezone.now().strftime('%Y-%m-%dT%H:%M')
    return render(request, 'events/announcement_form.html', {
        'default_created_at': default_created_at
    })

def edit_announcement(request, announcement_id):
    """Edit an existing announcement"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        return add_announcement(request)
    
    return render(request, 'events/announcement_form.html', {
        'announcement': announcement,
        'created_at_str': announcement.created_at.strftime('%Y-%m-%dT%H:%M')
    })

def delete_announcement(request, announcement_id):
    """Delete an announcement (AJAX)"""
    if not request.session.get('user_type') == 'admin':
        return JsonResponse({'status': 'unauthorized'}, status=401)
    
    if request.method == 'POST':
        try:
            announcement = Announcement.objects.get(id=announcement_id)
            announcement.delete()
            return JsonResponse({'status': 'success'})
        except Announcement.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    
    return JsonResponse({'status': 'invalid_method'}, status=400)

# ==================== STUDENT DASHBOARD ====================

def student_dashboard(request):
    """Student dashboard view"""
    if not request.session.get('user_type') == 'student':
        return redirect('admin_dashboard')
    
    try:
        student = Student.objects.get(id=request.session['student_name'])
    except Student.DoesNotExist:
        return redirect('logout')
    
    # Get student data
    my_participations = Participation.objects.filter(
        student=student, is_registered=True
    ).select_related('event').order_by('-participation_date')
    
    attended_events = Participation.objects.filter(
        student=student, attended=True
    ).select_related('event').order_by('-event__date')
    
    announcements = Announcement.objects.filter(
        target__in=['all', 'student']
    ).order_by('-created_at')
    
    context = {
        'student': student,
        'my_participations': my_participations,
        'attended_events': attended_events,
        'announcements': announcements,
    }
    return render(request, 'user/student_dashboard.html', context)

def register_event(request, event_id):
    """Register for an event (AJAX)"""
    if not request.session.get('student_name'):
        return JsonResponse({'success': False, 'message': 'User not authenticated'})
    
    event = get_object_or_404(Event, id=event_id)
    student = get_object_or_404(Student, id=request.session['student_name'])
    
    # Create or update participation
    participation, created = Participation.objects.update_or_create(
        student=student, event=event, defaults={'is_registered': True}
    )
    
    return JsonResponse({'success': True, 'message': 'Successfully registered for the event!'})

def mark_attendance(request, event_id):
    """Mark attendance for an event"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        attended_ids = request.POST.getlist('attended')
        
        # Update attendance records
        for participation in Participation.objects.filter(event=event):
            participation.attended = str(participation.student.id) in attended_ids
            participation.save()
        
        return redirect('view_event', event_id=event.id)
    
    # GET request
    participations = Participation.objects.filter(event=event).select_related('student')
    context = {'event': event, 'participations': participations}
    return render(request, 'events/mark_attendance.html', context)

def event_list(request):
    """Display events with filtering"""
    category = request.GET.get('category', 'all')
    now = timezone.now()
    events = Event.objects.filter(date__gte=now).order_by('date')
    
    if category != 'all' and category != 'upcoming':
        events = events.filter(category=category)
    
    # Get registered events for current student
    registered_event_ids = []
    if request.session.get('user_type') == 'student':
        try:
            student = Student.objects.get(id=request.session['student_name'])
            registered_event_ids = Participation.objects.filter(
                student=student, is_registered=True
            ).values_list('event_id', flat=True)
        except Student.DoesNotExist:
            pass
    
    context = {
        'events': events,
        'active_category': category,
        'registered_event_ids': list(registered_event_ids),
    }
    return render(request, 'events/after_events.html', context)

def event_participants(request, event_id):
    """View event participants"""
    if not request.session.get('user_type') == 'admin':
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id)
    participants = Participation.objects.filter(event=event, is_registered=True).select_related('student')
    
    context = {
        'event': event,
        'participants': participants,
    }
    return render(request, 'events/event_participants.html', context)
