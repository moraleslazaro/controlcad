# -*- coding: utf-8 -*-
from django.template.response import TemplateResponse
from django.template.context import RequestContext
from django.contrib import messages
from scan.models import check_image, image_exists, SingleImageDraw, ImageDraw, RelationImageDraw, SchemaImageDraw
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from database_storage import DatabaseStorage
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from admin.views import user_isnt_superuser
from django.db.models import Q
from cad.models import Codificator, guess_codificator, check_filename
import mimetypes
from django.conf import settings


#
# Single draws related views.
#
@user_passes_test(user_isnt_superuser)
def upload_single(request):
    context = RequestContext(request)

    if request.method == 'POST':
        if not request.FILES:
            messages.error(request, u"No ha seleccionado ningún fichero.")
            return TemplateResponse(request, 'scan/single/single_upload.html', context)

        # Retrieve the uploaded file
        upload = request.FILES.get('file')

        # Tune filename
        upload.name = check_filename(upload.name)

        # Check content type
        if not check_image(upload.name):
            messages.error(request, u"El fichero seleccionado no es válido.")
            return TemplateResponse(request, 'scan/single/single_upload.html', context)

        # Check if file already exists
        # BUG: Due to a bug on database integrity filename must be checked on every
        # namespace.
        if image_exists(upload.name):
            messages.error(request, u"El fichero seleccionado ya existe en el sistema.")
            return TemplateResponse(request, 'scan/single/single_upload.html', context)

        # Uploaded file is a valid image, save it!

       # Check file size.(Less than 1 MB allowed)
        if upload.size >= 1048576:
            messages.error(request, u"El fichero excede el tamaño máximo de 1 MB.")
            return TemplateResponse(request, 'scan/single/single_upload.html', context)

        image_draw = SingleImageDraw(
            filename=upload.name,
            content_type=check_image(upload.name),
            author=request.user,
            denomination=request.GET.get('denomination'),
            codificator=guess_codificator(upload.name),
            image=request.FILES.get('file'),
            number=upload.name.split('.')[0]
        ).save()

        messages.info(request, u"El plano '%s' ha sido subido." % upload.name)
        return HttpResponseRedirect(reverse('scan.views.list_single', urlconf='scan.urls'), context)

    return TemplateResponse(request, 'scan/single/single_upload.html', context)


@user_passes_test(user_isnt_superuser)
def list_single(request):
    context = RequestContext(request)

    draw_list = SingleImageDraw.objects.all()  # Get all single image draws

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        draw_list = SingleImageDraw.objects.filter(
            Q(number__icontains=query_string) | Q(denomination__icontains=query_string)
        )
        context.update({'query': query_string})

    # Enable pagination.
    paginator = Paginator(draw_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        draws = paginator.page(page)
    except PageNotAnInteger:
        draws = paginator.page(1)
    except EmptyPage:
        draws = paginator.page(paginator.num_pages)

    context.update({'draws': draws})
    return TemplateResponse(request, 'scan/single/single_list.html', context)


@user_passes_test(user_isnt_superuser)
def show_single_info(request, number):
    context = RequestContext(request)
    context.update({'draw': SingleImageDraw.objects.get(number=number)})  # TODO: Get object or 404
    context.update({'codificators': Codificator.objects.all()})
    return TemplateResponse(request, 'scan/single/single_details_info.html', context)


@user_passes_test(user_isnt_superuser)
def show_single_preview(request, number):
    context = RequestContext(request)

    context.update({'draw': SingleImageDraw.objects.get(number=number)})  # TODO: Get object or 404

    return TemplateResponse(request, 'scan/single/single_details_preview.html', context)


@user_passes_test(user_isnt_superuser)
def print_single(request, number):
    context = RequestContext(request)

    context.update({'draw': SingleImageDraw.objects.get(number=number)})  # TODO: Get object or 404

    return TemplateResponse(request, 'scan/single/single_print.html', context)


@user_passes_test(user_isnt_superuser)
def update_single(request, number):
    context = RequestContext(request)

    if request.method == 'POST':
        # Retrieve data
        denomination = request.POST.get('denomination', '')
        codificator = request.POST.get('codificator', '')

        draw = SingleImageDraw.objects.get(number=number)  # TODO: Get object or 404
        draw.denomination = denomination
        draw.codificator = Codificator.objects.get(pk=codificator)
        draw.save()
        messages.info(request, u"La información del plano '%s' ha sido actualizada." % draw.filename)
        return HttpResponseRedirect(reverse('scan.views.list_single', urlconf='scan.urls'), context)

    return HttpResponseRedirect(reverse('scan.views.show_single_info', urlconf='scan.urls', kwargs={'number': number}),
                                context)


@user_passes_test(user_isnt_superuser)
def single_inline(request, filename):
    """Return an inline image file or show 404 error page"""
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    image = storage.open('single/' + filename, 'rb')

    # Check if image exist
    if not image:
        return Http404()

    image_content = image.read()  # Read image

    # Prepare response
    # Guess mimetype and encoding from filename
    content_type, content_encoding = mimetypes.guess_type(filename)
    response = HttpResponse(content=image_content, content_type=content_type)
    response['Content-Disposition'] = 'inline; filename=%s' % filename

    # Check encoding
    if content_encoding:
        response['Content-Encoding'] = content_encoding

    return response


@user_passes_test(user_isnt_superuser)
def single_download(request, filename):
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    image = storage.open('single/' + filename, 'rb')

    # Check if image exists
    if not image:
        return Http404()

    image_content = image.read()  # Read image

    # Prepare response
    # Guess mimetype and encoding from filename
    content_type, content_encoding = mimetypes.guess_type(filename)
    response = HttpResponse(content=image_content, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    # Check encoding
    if content_encoding:
        response['Content-Encoding'] = content_encoding

    return response


@user_passes_test(user_isnt_superuser)
def delete_single(request, filename):
    image = SingleImageDraw.objects.get(filename=filename)  # TODO: Get object or 404
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    storage.delete('single/' + filename)
    image.delete()
    messages.info(request, u"El plano '%s' ha sido eliminado." % filename)
    return HttpResponseRedirect(reverse('scan.views.list_single', urlconf='scan.urls'))


#
# Relation draws related views
#
@user_passes_test(user_isnt_superuser)
def upload_relation(request):
    context = RequestContext(request)

    if request.method == 'POST':
        if not request.FILES:
            messages.error(request, u"No ha seleccionado ningún fichero.")
            return TemplateResponse(request, 'scan/relation/relation_upload.html', context)

        # Retrieve the uploaded file
        upload = request.FILES.get('file')

        # Tune filename
        upload.name = check_filename(upload.name)

        # Check content type
        if not check_image(upload.name):
            messages.error(request, u"El fichero seleccionado no es válido")
            return TemplateResponse(request, 'scan/relation/relation_upload.html', context)

        # Check if file already exists
        if image_exists(upload.name):
            messages.error(request, u"El fichero seleccionado ya existe en el sistema.")
            return TemplateResponse(request, 'scan/relation/relation_upload.html', context)

        # Check file size.(Less than 1 MB allowed)
        if upload.size >= 1048576:
            messages.error(request, u"El fichero excede el tamaño máximo de 1 MB.")
            return TemplateResponse(request, 'scan/relation/relation_upload.html', context)

        relation_draw = RelationImageDraw(
            filename=upload.name,
            content_type=check_image(upload.name),
            author=request.user,
            reference=request.POST.get('reference').upper(),
            type=request.POST.get('type'),
            code=upload.name.split('.')[0],
            image=upload
        ).save()

        messages.info(request, u"El plano '%s' ha sido subido." % upload.name)
        return HttpResponseRedirect(reverse('scan.views.list_relation', urlconf='scan.urls'))

    return TemplateResponse(request, 'scan/relation/relation_upload.html', context)


@user_passes_test(user_isnt_superuser)
def list_relation(request):
    context = RequestContext(request)
    draw_list = RelationImageDraw.objects.all()

    # Associate every single item on `draw_list` with available schemas.
    # This code is very nasty but resolve the problem.
    for draw in draw_list:
        try:
            associate_schema = SchemaImageDraw.objects.get(reference=draw.reference)
            draw.schema = associate_schema
        except SchemaImageDraw.DoesNotExist:
            draw.schema = ''

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        draw_list = draw_list.filter(Q(code__icontains=query_string) | Q(reference__icontains=query_string))

        # Associate again every single item on `draw_list` with available schemas.
        # This code is very nasty but resolve the problem.
        for draw in draw_list:
            try:
                associate_schema = SchemaImageDraw.objects.get(reference=draw.reference)
                draw.schema = associate_schema
            except SchemaImageDraw.DoesNotExist:
                draw.schema = ''

        context.update({'query': query_string})

    # Enable pagination
    paginator = Paginator(draw_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        draws = paginator.page(page)
    except PageNotAnInteger:
        draws = paginator.page(1)
    except EmptyPage:
        draws = paginator.page(paginator.num_pages)

    context.update({'draws': draws})
    return TemplateResponse(request, 'scan/relation/relation_list.html', context)


@user_passes_test(user_isnt_superuser)
def show_relation_preview(request, code):
    context = RequestContext(request)
    draw = RelationImageDraw.objects.get(code=code)  # TODO: Get object or 404
    context.update({'draw': draw})

    try:
        # Try to get the associate schema base on the `reference`
        associate_schema = SchemaImageDraw.objects.get(reference=draw.reference)
        context.update({'schema': associate_schema})
    except SchemaImageDraw.DoesNotExist:
        context.update({'schema': ''})

    return TemplateResponse(request, 'scan/relation/relation_details_preview.html', context)


@user_passes_test(user_isnt_superuser)
def print_relation(request, code):
    context = RequestContext(request)
    draw = RelationImageDraw.objects.get(code=code)  # TODO: Get object or 404
    context.update({'draw': draw})

    return TemplateResponse(request, 'scan/relation/relation_print.html', context)


@user_passes_test(user_isnt_superuser)
def show_relation_schema(request, code):
    context = RequestContext(request)
    draw = RelationImageDraw.objects.get(code=code)  # TODO: Get object or 404
    context.update({'draw': draw})

    try:
        # Try to get the associate schema base on the `reference`
        associate_schema = SchemaImageDraw.objects.get(reference=draw.reference)
        context.update({'schema': associate_schema})
    except SchemaImageDraw.DoesNotExist:
        context.update({'schema': ''})

    return TemplateResponse(request, 'scan/relation/relation_details_schema.html', context)


@user_passes_test(user_isnt_superuser)
def show_relation_info(request, code):
    context = RequestContext(request)
    draw = RelationImageDraw.objects.get(code=code)  # Get draw TODO: Get object or 404
    context.update({'draw': draw})

    try:
        # Try to get the associate schema base on the `reference`
        associate_schema = SchemaImageDraw.objects.get(reference=draw.reference)
        context.update({'schema': associate_schema})
    except SchemaImageDraw.DoesNotExist:
        context.update({'schema': ''})

    return TemplateResponse(request, 'scan/relation/relation_details_info.html', context)


@user_passes_test(user_isnt_superuser)
def update_relation(request, code):
    context = RequestContext(request)

    if request.method == 'POST':
        relation = RelationImageDraw.objects.get(code=code)  # TODO: Get object or 404
        relation.type = request.POST.get('type')
        relation.reference = request.POST.get('reference').upper();
        relation.save()
        messages.info(request, u"La información del plano '%s' ha sido actualizada." % relation.filename)
        return HttpResponseRedirect(reverse('scan.views.list_relation', urlconf='scan.urls'), context)

    # If no POST request has been made redirect to info page
    return HttpResponseRedirect(
        reverse('scan.views.show_relation_info', urlconf='scan.urls', kwargs={'code': code}),
        context
    )
            

@user_passes_test(user_isnt_superuser)
def relation_inline(request, filename):
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    image = storage.open('relation/' + filename, 'rb')

    # Check if image exist
    if not image:
        return Http404()

    image_content = image.read()  # Read image

    # Prepare response
    # Guess mimetype and encoding from filename
    content_type, content_encoding = mimetypes.guess_type(filename)
    response = HttpResponse(content=image_content, content_type=content_type)
    response['Content-Disposition'] = 'inline; filename=%s' % filename

    # Check encoding
    if content_encoding:
        response['Content-Encoding'] = content_encoding

    return response


@user_passes_test(user_isnt_superuser)
def relation_download(request, filename):
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    image = storage.open('relation/' + filename, 'rb')

    # Check if file exists
    if not image:
        return Http404()

    image_content = image.read()  # Read file content

    # Prepare response
    # Guess mimetype and encoding from filename
    content_type, content_encoding = mimetypes.guess_type(filename)
    response = HttpResponse(content=image_content, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    if content_encoding:
        response['Content-Encoding'] = content_encoding

    return response


@user_passes_test(user_isnt_superuser)
def delete_relation(request, filename):
    image = RelationImageDraw.objects.get(filename=filename) # TODO: Get object or 404
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    storage.delete('relation/' + filename)
    image.delete()
    messages.info(request, u"El plano '%s' ha sido eliminado." % filename)
    return HttpResponseRedirect(reverse('scan.views.list_relation', urlconf='scan.urls'))


#
# Schema draws related views.
#
@user_passes_test(user_isnt_superuser)
def list_schema(request):
    context = RequestContext(request)
    draw_list = SchemaImageDraw.objects.all()

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        draw_list = SchemaImageDraw.objects.filter(
            Q(reference__icontains=query_string) | Q(model__icontains=query_string)
        )
        context.update({'query': query_string})

    # Enable pagination.
    paginator = Paginator(draw_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        draws = paginator.page(page)
    except PageNotAnInteger:
        draws = paginator.page(1)
    except EmptyPage:
        draws = paginator.page(paginator.num_pages)

    context.update({'draws': draws})
    return TemplateResponse(request, 'scan/schema/schema_list.html', context)


@user_passes_test(user_isnt_superuser)
def upload_schema(request):
    context = RequestContext(request)

    if request.method == 'POST':
        if not request.FILES:
            messages.error(request, u"No ha seleccionado ningún fichero.")
            return TemplateResponse(request, 'scan/schema/schema_upload.html', context)

        # Retrieve the uploaded file.
        upload = request.FILES.get('file')

        # Tune filename
        upload.name = check_filename(upload.name)

        # Check file content.
        if not check_image(upload.name):
            messages.error(request, u"El fichero seleccionado no es válido.")
            return TemplateResponse(request, 'scan/schema/schema_upload.html', context)

        # Check if file already exists
        if image_exists(upload.name):
            messages.error(request, u"El fichero seleccionado ya existe en el sistema.")
            return TemplateResponse(request, 'scan/schema/schema_upload.html', context)

        # Check file size.(Less than 1 MB allowed)
        if upload.size >= 1048576:
            messages.error(request, u"El fichero excede el tamaño máximo de 1 MB.")
            return TemplateResponse(request, 'scan/schema/schema_upload.html', context)

        schema_draw = SchemaImageDraw(
            filename=upload.name,
            content_type=check_image(upload.name),
            author=request.user,
            reference=upload.name.split('.')[0],
            model=request.POST.get('model').upper(),
            image=upload
        )

        # Try to guess the codificator based on the reference
        if guess_codificator(schema_draw.reference):
            schema_draw.codificator = guess_codificator(schema_draw.reference)

        # Save the schema.
        schema_draw.save()

        messages.info(request, u"El plano '%s' ha sido subido." % upload.name)
        return HttpResponseRedirect(reverse('scan.views.list_schema', urlconf='scan.urls'))

    return TemplateResponse(request, 'scan/schema/schema_upload.html', context)


@user_passes_test(user_isnt_superuser)
def show_schema_info(request, reference):
    context = RequestContext(request)
    draw = SchemaImageDraw.objects.get(reference=reference)  # TODO: Get object or 404
    context.update({'draw': draw})
    context.update({'codificators': Codificator.objects.all()})

    return TemplateResponse(request, 'scan/schema/schema_details_info.html', context)


@user_passes_test(user_isnt_superuser)
def show_schema_preview(request, reference):
    context = RequestContext(request)
    draw = SchemaImageDraw.objects.get(reference=reference)  # TODO: Get object or 404
    context.update({'draw': draw})

    return TemplateResponse(request, 'scan/schema/schema_details_preview.html', context)


@user_passes_test(user_isnt_superuser)
def print_schema(request, reference):
    context = RequestContext(request)
    draw = SchemaImageDraw.objects.get(reference=reference)  # TODO: Get object or 404
    context.update({'draw': draw})

    return TemplateResponse(request, 'scan/schema/schema_print.html', context)


@user_passes_test(user_isnt_superuser)
def update_schema(request, reference):
    context = RequestContext(request)

    if request.method == 'POST':
        schema = SchemaImageDraw.objects.get(reference=reference)  # TODO: Get object or 404
        schema.model = request.POST.get('model').upper()
        codificator_code = request.POST.get('codificator', '')
        if codificator_code != '':
            # If a codificator has been selected update schema.
            schema.codificator = Codificator.objects.get(code=codificator_code)
        schema.save()
        messages.info(request, u"La información del plano '%s' ha sido actualizada." % schema.filename)
        return HttpResponseRedirect(reverse('scan.views.list_schema', urlconf='scan.urls'), context)

    # If no POST request has been made, redirect to info page.
    return HttpResponseRedirect(
        reverse('scan.views.show_schema_info', urlconf='scan.urls', kwargs={'reference': reference}),
        context
    )


@user_passes_test(user_isnt_superuser)
def schema_download(request, filename):
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    image = storage.open('schema/' + filename, 'rb')

    # Check if file exists
    if not image:
        return Http404()

    image_content = image.read()  # Read file content

    # Prepare response
    # Guess mimetype and encoding from filename
    content_type, content_encoding = mimetypes.guess_type(filename)
    response = HttpResponse(content=image_content, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    if content_encoding:
        response['Content-Encoding'] = content_encoding

    return response


@user_passes_test(user_isnt_superuser)
def schema_inline(request, filename):
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    image = storage.open('schema/' + filename, 'rb')

    # Check if image exist
    if not image:
        return Http404()

    image_content = image.read()  # Read image

    # Prepare response
    # Guess mimetype and encoding from filename
    content_type, content_encoding = mimetypes.guess_type(filename)
    response = HttpResponse(content=image_content, content_type=content_type)
    response['Content-Disposition'] = 'inline; filename=%s' % filename

    # Check encoding
    if content_encoding:
        response['Content-Encoding'] = content_encoding

    return response


@user_passes_test(user_isnt_superuser)
def delete_schema(request, filename):
    image = SchemaImageDraw.objects.get(filename=filename)  # TODO: Get object or 404
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    storage.delete('schema/' + filename)
    image.delete()
    messages.info(request, u"El plano '%s' ha sido eliminado." % filename)
    return HttpResponseRedirect(reverse('scan.views.list_schema', urlconf='scan.urls'))
