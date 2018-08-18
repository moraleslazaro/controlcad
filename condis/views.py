from django.template.context import RequestContext
from django.template.response import TemplateResponse
from condis.models import Equip
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from admin.views import user_isnt_superuser
from django.conf import settings
from scan.models import SchemaImageDraw
from django.db.models import Q


@user_passes_test(user_isnt_superuser)
def list_equips(request):
    context = RequestContext(request)

    if 'q' in request.GET:
        # Apply the filter if a query has been made.
        query_string = request.GET.get('q')
        equips_list = Equip.objects.filter(
            Q(codequipo__icontains=query_string) | Q(codmodelo__icontains=query_string)
        )
        # FIXME: Due to a problem with codequipo all entries that contains
        # a forward slash should be removed from the QuerySet.
        equips_list = equips_list.exclude(codequipo__icontains='/')
        context.update({'query': query_string})
    else:
        equips_list = Equip.objects.all()

    # Pagination
    paginator = Paginator(equips_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        equips = paginator.page(page)
    except PageNotAnInteger:
        equips = paginator.page(1)
    except EmptyPage:
        equips = paginator.page(paginator.num_pages)

    # Check if equips contain schemas.
    for equip in equips:
        if SchemaImageDraw.objects.filter(model=equip.codmodelo).count() == 0:
            equip.has_schemas = False
        else:
            equip.has_schemas = True

    context.update({'equips': equips})
    return TemplateResponse(request, 'equips/equips_list.html', context)


@user_passes_test(user_isnt_superuser)
def show_equip_info(request, codequipo):
    context = RequestContext(request)
    equip = Equip.objects.get(codequipo=codequipo)
    context.update({'equip': equip})

    schema_list = SchemaImageDraw.objects.filter(model=equip.codmodelo)
    paginator = Paginator(schema_list, 6)
    page = request.GET.get('page')

    try:
        schemas = paginator.page(page)
    except PageNotAnInteger:
        schemas = paginator.page(1)
    except EmptyPage:
        schemas = paginator.page(paginator.num_pages)

    context.update({'schemas': schemas})
    return TemplateResponse(request, 'equips/equips_details_info.html', context)