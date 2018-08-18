#-*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth, messages
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponse
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from admin.models import User
from django.db.models import Q
from cad.models import Dwg
from scan.models import ImageDraw


# Utilities functions for security on views.
# This functions are passed as arguments for
# user_passes_test decorator.
# Superuser is only for administrative tasks.
def user_is_dib(user):
    """Check if logged user's role is DIB"""
    if user.is_anonymous() or user.is_superuser:
        return False
    return 'DIB' in user.role


def user_is_pro(user):
    """Check if logged user's role is PRO"""
    if user.is_anonymous() or user.is_superuser:
        return False
    return 'PRO' in user.role


def user_is_ing(user):
    """Check if logged user's role is ING"""
    if user.is_anonymous() or user.is_superuser:
        return False
    return 'ING' in user.role


def user_isnt_dib(user):
    """Check if logged user's role isn't DIB. Should be ING or PRO"""
    if user.is_anonymous() or user.is_superuser:
        return False
    return ('PRO' in user.role) or ('ING' in user.role)


def user_is_admin_or_superuser(user):
    if user.is_anonymous():
        return False
    return user.is_superuser or user.is_admin


def user_isnt_superuser(user):
    if user.is_anonymous() or user.is_superuser:
        return False
    return True


@csrf_protect
def login(request):
    """
    Handle the login action.
    """

    redirect_to = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)
    context = {
        'next': redirect_to
    }

    # If user is already logged then redirect him to main page.
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('cad.views.start_view', urlconf='cad.urls'))

    # Log the user in through an Ajax Request.
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # If ``remember_me`` is not checked then do not
        # store the cookie.
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # If user isn't active return 'NOT FOUND'
            if not user.is_active:
                return HttpResponseNotFound()
            # OK, security check complete. Log the user in.
            auth.login(request, user)
            return HttpResponse()  # Return a 200 response
        else:
            # Unauthorized
            return HttpResponseNotFound()
    else:
        return TemplateResponse(request, 'login.html', context)


def logout(request):
    """
    Log out user
    """
    auth.logout(request)  # Don't worry if user isn't log in.
    return HttpResponseRedirect(reverse('cad.views.start_view', urlconf='cad.urls'))


@login_required
def logged_user_change_password(request):
    context = RequestContext(request)

    if request.method == 'POST':
        redirect_to = request.POST.get('previous')
        context.update({'previous': redirect_to})

        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()  # Save changes to database.
            messages.info(request, u'La contraseña ha sido cambiada con éxito.')
            return HttpResponseRedirect(reverse('admin.views.logged_user_account_info', urlconf='admin.urls'), context)

    return TemplateResponse(request, 'user/user_change_password.html')


@login_required
def logged_user_account_info(request):
    context = RequestContext(request)

    if request.method == 'POST':
        user = request.user

        try:
            User.objects.get(username=request.POST.get('username'))
        except User.DoesNotExist:
             # Retrieve data.
            user.username = request.POST.get('username', user.username)
            user.first_name = request.POST.get('first-name', user.first_name)
            user.last_name = request.POST.get('last-name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            messages.info(request, u"La información del usuario '%s' ha sido actualizada." % user.username)
            return HttpResponseRedirect(reverse('cad.views.start_view', urlconf='cad.urls'), context)

        if User.objects.get(username=request.POST.get('username')) and \
                User.objects.get(username=request.POST.get('username')).username == request.user.username:
             # Retrieve data.
            user.username = request.POST.get('username', user.username)
            user.first_name = request.POST.get('first-name', user.first_name)
            user.last_name = request.POST.get('last-name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            messages.info(request, u"La información del usuario '%s' ha sido actualizada." % user.username)
            return HttpResponseRedirect(reverse('cad.views.start_view', urlconf='cad.urls'), context)
        else:
            messages.error(request, u"El nombre de usuario '%s' ya existe." % request.POST.get('username'))
            return TemplateResponse(request, 'user/user_account_info.html', context)

    return TemplateResponse(request, 'user/user_account_info.html', context)


#
# Admin related views
#
@user_passes_test(user_is_admin_or_superuser)
def admin_user_list(request):
    context = RequestContext(request)
    # Retrieve all users except admin and inactive users.
    user_list = User.objects.exclude(username='admin').exclude(is_active=False)

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        user_list = User.objects.filter(
            Q(username__icontains=query_string) | Q(first_name__icontains=query_string) |
            Q(last_name__icontains=query_string) | Q(email__icontains=query_string)
        )
        context.update({'query': query_string})

    # Pagination
    paginator = Paginator(user_list, 15)
    page = request.GET.get('page')

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context.update({'users': users})

    return TemplateResponse(request, 'admin/admin_users_list.html', context)


@user_passes_test(user_is_admin_or_superuser)
def admin_user_add(request):
    context = RequestContext(request)
    new_user = User()

    if request.method == 'POST':
        # Retrieve data.
        new_user.username = request.POST.get('username')
        new_user.first_name = request.POST.get('first-name')
        new_user.last_name = request.POST.get('last-name')
        new_user.email = request.POST.get('email')

        if request.POST.get('rol', ''):
            new_user.is_admin = True

        new_user.role = request.POST.get('role')

        # Check if username already exists.
        try:
            User.objects.get(username=request.POST.get('username'))
        except User.DoesNotExist:
            # Password verification
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')
            if password == confirm_password:
                new_user.set_password(password)
            else:
                messages.error(request, u"Las contraseñas no coinciden.", context)
                return TemplateResponse(request, 'admin/admin_users_add.html', context)

            # Save user!
            new_user.save()
            messages.info(request, u"El usuario '%s' ha sido creado." % new_user.username)
            return HttpResponseRedirect(reverse('admin.views.admin_user_list', urlconf='admin.urls'), context)

        # If username exist notify user.
        if User.objects.get(username=request.POST.get('username')):
            context.update({'new_user': new_user})
            messages.error(request, u"El nombre de usuario '%s' ya existe." % request.POST.get('username'))
            return TemplateResponse(request, 'admin/admin_users_add.html', context)

    return TemplateResponse(request, 'admin/admin_users_add.html', context)


@user_passes_test(user_is_admin_or_superuser)
def admin_user_edit(request, id):
    context = RequestContext(request)
    user = User.objects.get(id=id)
    context.update({'selected_user': user})

    if request.method == 'POST':
        # Retrieve data
        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first-name', user.first_name)
        user.last_name = request.POST.get('last-name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)

        if request.POST.get('is-admin', ''):
            user.is_admin = True
        else:
            user.is_admin = False

        try:
            User.objects.get(username=request.POST.get('username'))
        except User.DoesNotExist:
            user.save()
            messages.info(request, u"La información del usuario '%s' ha sido actualizada." % user.username)
            return HttpResponseRedirect(reverse('admin.views.admin_user_list', urlconf='admin.urls'), context)

        if User.objects.get(username=request.POST.get('username')) and \
                User.objects.get(username=request.POST.get('username')).username == User.objects.get(id=id).username:
            user.save()
            messages.info(request, u"La información del usuario '%s' ha sido actualizada." % user.username)
            return HttpResponseRedirect(reverse('admin.views.admin_user_list', urlconf='admin.urls'), context)
        else:
            messages.error(request, u"El nombre de usuario '%s' ya existe." % request.POST.get('username'))
            return TemplateResponse(request, 'admin/admin_users_show.html', context)

    return TemplateResponse(request, 'admin/admin_users_show.html', context)


@user_passes_test(user_is_admin_or_superuser)
def admin_user_change_password(request, id):
    context = RequestContext(request)
    user = User.objects.get(id=id)
    context.update({'selected_user': user})

    if request.method == 'POST':
        password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.info(request, u"La contraseña ha sido cambiada con éxito.")
            return HttpResponseRedirect(
                reverse('admin.views.admin_user_edit', urlconf='admin.urls', kwargs={'id': user.id}),
                context
            )

    return TemplateResponse(request, 'admin/admin_users_change_password.html', context)


@user_passes_test(user_is_admin_or_superuser)
def admin_user_delete(request, username):
    user = get_object_or_404(User, username=username)

    # Enforcing security
    if request.user == user:
        return HttpResponseNotFound()

    # If user have associated files don't delete it
    if user.uploaded_files.count() or user.published_files.count() or user.imagedraw_set.count():
        user.is_active = False
        user.save()
    else:
        user.delete()

    # Notify user.
    messages.info(request, u"El usuario '%s' ha sido eliminado." % username)
    return HttpResponseRedirect(reverse('admin.views.admin_user_list', urlconf='admin.urls'))


@user_passes_test(user_is_admin_or_superuser)
def admin_show_dashboard(request):
    context = RequestContext(request)

    # Column chart data.
    # Draws per versions processing
    dwg_versions = list()
    dwg_versions_desc = list()

    # Convert DWG_VERSIONS into a nice list
    # with only version descriptions.
    for item in Dwg.DWG_VERSIONS:
        dwg_versions.append(item[0])
        dwg_versions_desc.append(item[1])

    dwg_versions_qty = list()
    for item in dwg_versions:
        items = Dwg.objects.filter(compatibility=item)
        dwg_versions_qty.append(items.count())

    context.update({'dwg_versions': dwg_versions})
    context.update({'dwg_versions_desc': dwg_versions_desc})
    context.update({'dwg_versions_qty': dwg_versions_qty})

    # Pie chart data.
    users_list = list()

    # For all users except those who aren't active and admin of course.
    for user in User.objects.all().exclude(is_active=False).exclude(username='admin'):
        # Calculate Per Cent.
        try:
            user.dwg_per_cent = (user.uploaded_files.count() + user.imagedraw_set.count()) * 100 / (
                Dwg.objects.count() + ImageDraw.objects.count())
        except ZeroDivisionError:
            user.dwg_per_cent = 0
        users_list.append(user)

    context.update({'users_list': users_list})

    #
    # Area chart data.
    #
    imagedraws_per_weekday = dict()
    dwg_per_weekday = dict()
    imagedraws_groups_per_day = dict()
    dwg_groups_per_day = dict()
    imagedraws_qty_per_weekday = dict()
    dwg_qty_per_weekday = dict()

    # Dictionary initialization in the form
    # {
    #   '0': list(),
    #   '1': list(),
    #    ...
    #   '6': list()
    # }
    for day in range(0, 7):
        imagedraws_per_weekday[day] = list()
        dwg_per_weekday[day] = list()
        imagedraws_groups_per_day[day] = list()
        dwg_groups_per_day[day] = list()
        imagedraws_qty_per_weekday[day] = list()
        dwg_qty_per_weekday[day] = list()

    # Fill dictionaries with data.
    # Example:
    # {
    #   '0': [<ImageDraw 1>, <ImageDraw2>],
    #   '1': [<ImageDraw 3>, <ImageDraw4>],
    #   ...
    #   '6': [<ImageDraw 5>, <ImageDraw6>]
    # }
    # ImageDraws
    for draw in ImageDraw.objects.all():
        for day in range(0, 7):
            if draw.date.weekday() == day:
                imagedraws_per_weekday[day].append(draw)

    # The same for Dwgs
    for dwg in Dwg.objects.all():
        for day in range(0, 7):
            if dwg.date.weekday() == day:
                dwg_per_weekday[day].append(dwg)

    # Work with groups in ImageDraws
    # Example:
    # {
    #   '0': [7,7,7,7,14,14,21,21,21,21,21],
    #   '1': [8,15,22,22,22,22,22],
    #   ...
    #   '6': [13,13,13,13,13,13,20,27]
    # }
    for items_per_weekday in imagedraws_per_weekday.values():
        if not items_per_weekday:
            # List is empty
            pass
        else:
            for item in items_per_weekday:
                for day in range(0, 7):
                    if (item.date.weekday() == day) and (item.date.day not in imagedraws_groups_per_day.values()):
                        imagedraws_groups_per_day[day].append(item.date.day)
                        break  # If day number is found, break loop.

    # The same for dwg
    for dwg_items_per_weekday in dwg_per_weekday.values():
        if not dwg_items_per_weekday:
            # List is empty
            pass
        else:
            for item in dwg_items_per_weekday:
                for day in range(0, 7):
                    if (item.date.weekday() == day) and (item.date.day not in dwg_groups_per_day.values()):
                        dwg_groups_per_day[day].append(item.date.day)
                        break  # If day number is found, break loop.

    # Count number of Draws per weekday
    for items_per_group in imagedraws_per_weekday.values():
        if not items_per_group:
            # List is empty
            pass
        else:
            for item in items_per_group:
                for day in range(0, 7):
                    if (item.date.weekday() == day) and not imagedraws_qty_per_weekday[day]:
                        # If is empty
                        imagedraws_qty_per_weekday[day].append(item.date.day)
                        break
                    elif (item.date.weekday() == day) and not item.date.day in imagedraws_qty_per_weekday[day]:
                        # Or don't exits.
                        imagedraws_qty_per_weekday[day].append(item.date.day)
                        break

    # The same for Dwgs.
    for items_per_group in dwg_per_weekday.values():
        if not items_per_group:
            # List is empty
            pass
        else:
            for item in items_per_group:
                for day in range(0, 7):
                    if (item.date.weekday() == day) and not dwg_qty_per_weekday[day]:
                        # If is empty
                        dwg_qty_per_weekday[day].append(item.date.day)
                        break
                    elif (item.date.weekday() == day) and not item.date.day in dwg_qty_per_weekday[day]:
                        # Or don't exists.
                        dwg_qty_per_weekday[day].append(item.date.day)
                        break

    # Calculate values
    imagedraw_chart_data = list()
    dwgs_chart_data = list()

    # Imagedraws.
    for day in range(0, 5):
        # Qty of draws uploaded on mondays / Qty of mondays
        if len(imagedraws_qty_per_weekday[day]) == 0:
            # Div by zero exception!
            means = 0
        else:
            means = len(imagedraws_per_weekday[day]) / len(imagedraws_qty_per_weekday[day])

        imagedraw_chart_data.append(means)

    # Dwgs
    for day in range(0, 5):
        # Qty of dwgs uploaded on mondays / Qty of mondays
        if len(dwg_qty_per_weekday[day]) == 0:
            means = 0
        else:
            means = len(dwg_per_weekday[day]) / len(dwg_qty_per_weekday[day])

        dwgs_chart_data.append(means)

    context.update({'dwg_data': dwgs_chart_data})
    context.update({'scan_data': imagedraw_chart_data})

    return TemplateResponse(request, 'admin/admin_dashboard.html', context)