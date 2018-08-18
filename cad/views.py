# -*- coding: utf-8 -*-
from django.template.context import RequestContext
from django.contrib import messages
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cad.models import Dwg, Draw, Codificator, dwg_exists, set_draw, check_filename
from admin.views import user_is_ing, user_isnt_dib
from django.conf import settings
from django.db.models import Q


# Main view, entry point of the application
def start_view(request):
    # If user is authenticated show `Main Page` or
    # `Start page` instead.
    if request.user.is_authenticated():
        # Return `Main Page`
        return HttpResponseRedirect(reverse('cad.views.list_draws', urlconf='cad.urls'))
    return TemplateResponse(request, 'start.html')


# Upload a DWG file
@login_required
def upload_dwg(request):
    context = RequestContext(request)

    # The GET value is used to fill the form the first
    # time the template is returned.
    previous_page = request.GET.get('previous', '')
    context.update({'previous': previous_page})

    if request.method == 'POST':
        if not request.FILES:
            messages.error(request, u"No ha seleccionado ningún fichero.")
            return TemplateResponse(request, 'cad/cad_upload.html', context)

        # Get the previous value from the form
        previous_page = request.POST.get('previous', '')

        # Retrieve uploaded file.
        upload = request.FILES.get('file')

        # Tune the filename
        upload.name = check_filename(upload.name)

        # Check if uploaded file exist.
        if dwg_exists(upload.read()):
            messages.error(request, u"El fichero seleccionado ya existe en el sistema.")
            return TemplateResponse(request, 'cad/cad_upload.html', context)

        upload.seek(0)  # Restore file pointer to the beginning.

        # Check if uploaded file is a valid DWG.
        try:
            pre_save.connect(set_draw, sender=Dwg)
            dwg = Dwg.objects.create_dwg(
                upload.name,
                upload.read(),
            )
        except ValidationError:
            messages.error(request, u"El fichero seleccionado no es válido.")
            return TemplateResponse(request, 'cad/cad_upload.html', context)

        # Include comment if exist and save file.
        dwg.comment = request.POST.get('comment', '')
        dwg.author = request.user

        # Check if uploaded file should be public.
        if request.POST.get('public', ''):
            dwg.public = True
            dwg.publisher = request.user   # Uploader is the publisher too.

        # Save it!
        dwg.save()

        # Notifify user
        if Dwg.objects.filter(filename=upload.name).count() > 1:
            # File updated.
            messages.info(request, u"El plano '%s' ha sido actualizado." % upload.name)
            return HttpResponseRedirect(previous_page, context)

        # If this is the first time.
        messages.info(request, u"El plano '%s' ha sido subido." % upload.name)
        return HttpResponseRedirect(previous_page, context)

    return TemplateResponse(request, 'cad/cad_upload.html', context)


# DWG listing.
@login_required
def list_draws(request):
    # This is the first view after login
    # If admin arrive here redirect him to dashboard.
    if request.user.role == 'DIB':
        context = RequestContext(request)

        draw_list = Draw.objects.all()  # Get all draws.

        if 'q' in request.GET:
            # Apply the filter if a query has been made.
            query_string = request.GET.get('q')
            draw_list = Draw.objects.filter(name__icontains=query_string)
            context.update({'query': query_string})

        # Set pagination.
        paginator = Paginator(draw_list, settings.ITEMS_PER_PAGE)
        page = request.GET.get('page')

        try:
            draws = paginator.page(page)
        except PageNotAnInteger:
            draws = paginator.page(1)
        except EmptyPage:
            draws = paginator.page(paginator.num_pages)

        context.update({'draws': draws})
        return TemplateResponse(request, 'cad/cad_list.html', context)

    elif request.user.role == 'PRO' or request.user.role == 'ING':
        return HttpResponseRedirect(reverse('cad.views.list_draws_public', urlconf='cad.urls'))
    elif request.user.is_superuser:
        return HttpResponseRedirect(reverse('admin.views.admin_show_dashboard', urlconf='admin.urls'))


@user_passes_test(user_isnt_dib)
def list_draws_inbox(request):
    context = RequestContext(request)

    dwg_list = Dwg.objects.filter(public=False).order_by('filename')

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        dwg_list = dwg_list.filter(filename__icontains=query_string)
        context.update({'query': query_string})

    # Set pagination.
    paginator = Paginator(dwg_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        dwgs = paginator.page(page)
    except PageNotAnInteger:
        dwgs = paginator.page(1)
    except EmptyPage:
        dwgs = paginator.page(paginator.num_pages)

    context.update({'dwgs': dwgs})
    return TemplateResponse(request, 'cad/cad_list_inbox.html', context)


@user_passes_test(user_isnt_dib)
def list_draws_public(request):
    context = RequestContext(request)

    draw_list = Draw.objects.all()  # Get all draws.
    inbox_count = Dwg.objects.filter(public=False).count()
    context.update({'inbox_count': inbox_count})

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        draw_list = Draw.objects.filter(name__icontains=query_string)
        context.update({'query': query_string})

    # Set pagination.
    paginator = Paginator(draw_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        draws = paginator.page(page)
    except PageNotAnInteger:
        draws = paginator.page(1)
    except EmptyPage:
        draws = paginator.page(paginator.num_pages)

    context.update({'draws': draws})

    return TemplateResponse(request, 'cad/cad_list_public.html', context)


# Make public a dwg.
@user_passes_test(user_isnt_dib)
def public_dwg(request, md5):
    dwg = get_object_or_404(Dwg, md5=md5)

    dwg.public = True
    dwg.publisher = request.user
    dwg.save()

    messages.info(request, u'El plano %s ha sido aprobado.' % dwg.filename)
    return HttpResponseRedirect(reverse('cad.views.list_draws_inbox', urlconf='cad.urls'))


# Draw info.
@login_required
def show_draw_info(request, name):
    context = RequestContext(request)

    context.update({
        'draw': Draw.objects.get(name=name),  # TODO: Get object or 404
        'codificators': Codificator.objects.all(),
    })

    return TemplateResponse(request, 'cad/cad_details_info.html', context)


# Draw's dwg versions.
@login_required
def show_draw_versions(request, name):
    context = RequestContext(request)
    context.update({'draw': Draw.objects.get(name=name)})  # TODO: Get object or 404

    # Get all dwgs from selected draw ordered by date.
    dwg_list = Draw.objects.get(name=name).dwg_set.all().order_by('-date')
    paginator = Paginator(dwg_list, 6)
    page = request.GET.get('page')

    try:
        dwgs = paginator.page(page)
    except PageNotAnInteger:
        dwgs = paginator.page(1)
    except EmptyPage:
        dwgs = paginator.page(paginator.num_pages)

    context.update({'dwgs': dwgs})
    return TemplateResponse(request, 'cad/cad_details_versions.html', context)


# Update Draw's information
@login_required
def update_draw(request, name):
    context = RequestContext(request)

    if request.method == 'POST':
        # Get data.
        codificator_code = request.POST.get('codificator', '')
        description = request.POST.get('description', '')

        # Update draw.
        draw = Draw.objects.get(name=name)  # TODO: Get object or 404
        if codificator_code != '':
            # If a codificator has been selected update draw
            draw.codificator = Codificator.objects.get(code=codificator_code)
        draw.description = description
        draw.save()
        messages.info(request, u"La información del plano '%s' ha sido actualizada." % draw.name)
        return HttpResponseRedirect(reverse('cad.views.list_draws_public', urlconf='cad.urls'), context)

    return HttpResponseRedirect(reverse('cad.views.show_draw', urlconf='cad.urls', kwargs={'name': name}), context)


# Delete a Draw
@user_passes_test(user_is_ing)
def delete_draw(request, name):
    draw = get_object_or_404(Draw, name=name)
    draw.delete()
    messages.info(request, u"El plano '%s' ha sido eliminado completamente." % name)
    return HttpResponseRedirect(reverse('cad.views.list_draws_public', urlconf='cad.urls'))


# Download a DWG or 404.
@login_required
def download_dwg(request, md5):
    dwg = get_object_or_404(Dwg, md5=md5)
    response = HttpResponse()
    response['content-type'] = "application/octect-stream"
    response['Content-Disposition'] = "attachment; filename=%s" % dwg.filename
    response.write(dwg.get_data())
    return response


# Delete a DWG
@user_passes_test(user_is_ing)
def delete_dwg(request, md5):
    dwg = get_object_or_404(Dwg, md5=md5)
    draw = dwg.draw  # Get Dwg's draw.
    dwg.delete()

    if not draw.dwg_set.count():
        # If no Dwg left then remove draw too.
        name = draw.name
        draw.delete()
        messages.info(request, u"El plano '%s' ha sido eliminado completamente." % name)
        return HttpResponseRedirect(reverse('cad.views.list_draws_public', urlconf='cad.urls'))

    messages.info(request, u"La versión ha sido eliminada.")
    return HttpResponseRedirect(
        reverse('cad.views.show_draw_versions', urlconf='cad.urls', kwargs={'name': draw.name})
    )


# Delete a DWG
@user_passes_test(user_is_ing)
def delete_inbox_dwg(request, md5):
    dwg = get_object_or_404(Dwg, md5=md5)
    draw = dwg.draw  # Get Dwg's draw.
    dwg.delete()

    if not draw.dwg_set.count():
        # If no Dwg left then remove draw too.
        name = draw.name
        draw.delete()

    messages.info(request, u"El plano seleccionado ha sido eliminado.")
    return HttpResponseRedirect(
        reverse('cad.views.list_draws_inbox', urlconf='cad.urls')
    )


# Views related to codificators
@user_passes_test(user_is_ing)
def list_codificators(request):
    context = RequestContext(request)

    codificator_list = Codificator.objects.all()

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        codificator_list = Codificator.objects.filter(
            Q(code__icontains=query_string) | Q(description__icontains=query_string)
        )
        context.update({'query': query_string})

    # Set pagination.
    paginator = Paginator(codificator_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        codificators = paginator.page(page)
    except PageNotAnInteger:
        codificators = paginator.page(1)
    except EmptyPage:
        codificators = paginator.page(paginator.num_pages)

    context.update({'codificators': codificators})
    return TemplateResponse(request, 'cod/cod_list.html', context)


@user_passes_test(user_is_ing)
def add_codificator(request):
    context = RequestContext(request)

    if request.method == 'POST':
        codificator = Codificator()
        codificator.code = request.POST.get('code')
        codificator.description = request.POST.get('description')
        codificator.save()
        messages.info(request, u'El codificador ha sido creado.')
        return HttpResponseRedirect(reverse('cad.views.list_codificators', urlconf='cad.urls'))

    return TemplateResponse(request, 'cod/cod_add.html', context)


@user_passes_test(user_is_ing)
def edit_codificator(request, code):
    context = RequestContext(request)
    codificator = get_object_or_404(Codificator, code=code)
    context.update({'codificator': codificator})

    if request.method == 'POST':
        codificator.code = request.POST.get('code')
        codificator.description = request.POST.get('description')
        codificator.save()
        messages.info(request, u'El codificador ha sido actualizado.')
        return HttpResponseRedirect(reverse('cad.views.list_codificators', urlconf='cad.urls'))

    return TemplateResponse(request, 'cod/cod_edit.html', context)


@user_passes_test(user_is_ing)
def delete_codificator(request, code):
    context = RequestContext(request)
    codificator = get_object_or_404(Codificator, code=code)

    if codificator.draw_set.count() and codificator.imagedraw_set.count():
        codificator.deleted = True
        messages.info(request, u'El codificador seleccionado ha sido eliminado.')
        return HttpResponseRedirect(reverse('cad.views.list_codificators', urlconf='cad.urls'))

    codificator.delete()
    messages.info(request, u'El codificador seleccionado ha sido eliminado.')
    return HttpResponseRedirect(reverse('cad.views.list_codificators', urlconf='cad.urls'))

