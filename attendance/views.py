from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views import generic
from django.views.generic.edit import FormView
from datetime import date

from .models import Class, Student, Session
from .forms import SignInForm, ChooseClassForm


class ClassView(FormView):
    template_name = 'attendance/class.html'
    form_class = ChooseClassForm
    success_url = '/attendance/signin/'

    def form_valid(self, form):
        c = form.cleaned_data['classes']
        return HttpResponseRedirect(self.get_success_url() + "?class=" + c.class_id)


class SignInView(FormView):
    template_name = 'attendance/signin.html'
    form_class = SignInForm


class ClassIndexView(generic.ListView):
    """
    Root View for classes
    """
    template_name = 'attendance/class_index.html'
    context_object_name = 'class_index'

    def get_queryset(self):
        classes = None
        if self.request.user.is_authenticated():
            classes = Class.objects.all()
        return classes


class TabulateView(generic.DetailView):
    """
    Tabulates Attendance Data for easy copying.  Next will be a rest interface to download it as a csv
    """
    template_name = 'attendance/tabulate.html'
    context_object_name = 'attendance_data'
    model = Class

    def get_context_data(self, **kwargs):
        context = super(TabulateView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            my_class = self.get_object()
            sessions = Session.objects.filter(session_class=my_class).order_by('date')
            students = Student.objects.filter(enrolled_class=my_class).order_by('last_name')
            context['sessions'] = sessions
            context['students'] = students
        return context


def verify(request):
    """
    Verifies student id, class, and password. If it all matches up, the student is marked present for the day.
    :param request:
    :return:
    """
    if request.GET:
        today = date.today()
        student = Student.objects.get(student_id=request.GET.get('student_id'))
        current_class = Class.objects.get(class_id=request.GET.get('class_id'))
        class_id = current_class.id
        sessions = Session.objects.filter(session_class=class_id).filter(date__exact=today)
        s = sessions[0]

        if s.students_present.filter(id=student.id).exists():
            return HttpResponse("You are already signed in")
        elif student.enrolled_class == current_class and request.GET.get('today_password') == s.password:
            s.students_present.add(student)
            s.save()
            return HttpResponse("Thank you, %s" % student.first_name)
        else:
            return HttpResponse("Password, Student ID, or Class incorrect")


def user_login(request):
    """
    Login request view
    :param request:
    :return:
    """

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/attendance/classes/')
            else:
                return HttpResponse('Your account is disabled')
        else:
            print('Invalid Login')
            return HttpResponse('Invalid login details')
    else:
        return render(request, 'attendance/login.html')


@login_required
def user_logout(request):
    """
    Logs current client out
    :param request:
    :return:
    """
    logout(request)
    return HttpResponseRedirect('/attendance/')
