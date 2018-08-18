from django.db import models
from django.utils import timezone
from django.conf import settings
from cad.models import Codificator
from database_storage import DatabaseStorage
import mimetypes


class ImageDraw(models.Model):
    # DatabaseStorage API options
    DBS_OPTIONS = {
        'table': 'scan_files',
        'base_url': '/'
    }

    # Supported image formats.
    MIMETYPES = (
        ('image/x-png', 'PNG Image'),
        ('image/bmp', 'BMP Image'),
        ('image/pjpeg', 'JPEG Image'),
    )

    filename = models.CharField(max_length=80, primary_key=True)
    content_type = models.CharField(max_length=20, choices=MIMETYPES)
    codificator = models.ForeignKey(Codificator, null=True)
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return '%s - %s' % (self.filename, self.content_type)


class SingleImageDraw(ImageDraw):
    number = models.CharField(max_length=20, primary_key=True)
    denomination = models.CharField(max_length=80, null=True)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='single/',
        storage=DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    )

    def __unicode__(self):
        return u'%s' % self.number

    class Meta:
        ordering = ('number',)


class RelationImageDraw(ImageDraw):
    # Only for RelationImageDraw.
    DRAW_TYPE = (
        ('H', 'Horizontal'),
        ('V', 'Vertical')
    )

    code = models.CharField(max_length=20, primary_key=True)
    reference = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=DRAW_TYPE)

    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='relation/',
        storage=DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    )

    def __unicode__(self):
        return u'%s' % self.code

    class Meta:
        ordering = ('reference',)


class SchemaImageDraw(ImageDraw):
    reference = models.CharField(max_length=20, primary_key=True)
    model = models.CharField(max_length=20)

    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='schema/',
        storage=DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    )

    def __unicode__(self):
        return u'%s' % self.reference

    class Meta:
        ordering = ('reference',)


def image_exists(filename):
    """Check if image filename exists in the database."""
    # Read file from database
    storage = DatabaseStorage(options=ImageDraw.DBS_OPTIONS)
    # Check all namespaces
    check_single = storage.open('single/' + filename, 'rb')
    check_relation = storage.open('relation/' + filename, 'rb')
    check_schema = storage.open('schema/' + filename, 'rb')

    if check_single or check_relation or check_schema:
        return True
    return False


def check_image(filename):
    """Check if a image is valid and return the content type or None instead."""
    formats = list()
    content_type = mimetypes.guess_type(filename)[0]

    # Convert MIMETYPES into a nice list
    # with only mimetypes.
    for item in ImageDraw.MIMETYPES:
        formats.append(item[0])

    # Check if content type is included in the list
    if content_type in formats:
        return content_type
    return None