from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from hashlib import md5
from base64 import b64encode, b64decode
import zlib


class Draw(models.Model):
    name = models.CharField(max_length=40, primary_key=True)
    codificator = models.ForeignKey('Codificator', null=True)
    description = models.CharField(max_length=60, null=True)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        ordering = ('name',)


class DwgManager(models.Manager):
    def create_dwg(self, filename, data):
        """
        Creates a Dwg with the given `filename` and `data`.
        """

        if get_dwg_version(data) is None:
            raise ValidationError('Invalid DWG file')
        dwg = self.model()
        dwg.filename = filename
        dwg.set_data(data)
        return dwg


class Dwg(models.Model):
    # Supported DWG versions, for more details about DWG see:
    # http://en.wikipedia.org/wiki/.dwg
    DWG_VERSIONS = (
        ('AC1014', 'AutoCAD Release 14'),
        ('AC1015', 'AutoCAD 2000, 2000i, 2002'),
        ('AC1018', 'AutoCAD 2004, 2005, 2006'),
        ('AC1021', 'AutoCAD 2007, 2008, 2009'),
        ('AC1024', 'AutoCAD 2010, 2011, 2012'),
        ('AC1027', 'AutoCAD 2013'),
    )

    filename = models.CharField(max_length=80)
    size = models.IntegerField()
    comment = models.TextField()
    md5 = models.CharField(max_length=32, primary_key=True)
    compatibility = models.CharField(max_length=6, choices=DWG_VERSIONS)
    date = models.DateTimeField(default=timezone.now)
    data = models.TextField()
    draw = models.ForeignKey('Draw')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name="uploaded_files")
    public = models.BooleanField(default=False)
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name="published_files", null=True)

    objects = DwgManager()

    def set_data(self, data):
        """
        Compress and encode data using zlib and base64.
        """

        # Check if raw `data` is a DWG file
        if get_dwg_version(data) is None:
            raise ValidationError('Invalid DWG file')
            # Set some fields from `data` value
        self.compatibility = get_dwg_version(data)
        self.size = len(data)
        self.md5 = md5(data).hexdigest()
        self.data = b64encode(zlib.compress(data))

    def get_data(self):
        """Return raw `data`."""
        return zlib.decompress(b64decode(self.data))

    def __unicode__(self):
        return u'%s - %s' % (self.filename, self.md5)


class Codificator(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    description = models.CharField(max_length=60)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.code, self.description)


# Utility function to obtain the DWG version from file content.
def get_dwg_version(data):
    """
    Return DWG version or None instead.

    data - Raw file content
    """

    versions = list()

    # Convert DWG_VERSIONS into a nice list
    # with only version numbers.
    for item in Dwg.DWG_VERSIONS:
        versions.append(item[0])

    # Check if first 6 bytes of data
    # belongs to version list.
    if data[:6] in versions:
        return data[:6]
    else:
        return None


# Guess the codificator from a string.
def guess_codificator(string):
    """
    Return the corresponding codificator object or None instead
    """
    codificators = list()

    # Get only codificator codes.
    for i in Codificator.objects.values_list():
        codificators.append(i[0])

    if string[0] in codificators:
        # Check first character against the list.
        return Codificator.objects.get(code=string[0])

    if string[0:2] in codificators:
        # Check first two character again the list.
        return Codificator.objects.get(code=string[0:2])

    # Not found coincidence.
    return None


# Signal pre_save for create or update a Draw object from Dwg save method.
def set_draw(instance, **kwargs):
    """
    Create or set a Draw object from Dwg save method.
    """

    name = instance.filename.split('.')[0]
    if not Draw.objects.filter(name__icontains=name):
        # Create a Draw if not exists
        draw = Draw(name=name)
        instance.draw = draw
        # Try to guess the codificator based on name
        if guess_codificator(draw.name):
            draw.codificator = guess_codificator(draw.name)

        draw.save()
    else:
        instance.draw = Draw.objects.get(name=name)
        if guess_codificator(instance.draw.name):
            instance.codificator = guess_codificator(instance.draw.name)


# Check if a DWG file content exists in the database.
def dwg_exists(content):
    """
    Return True if DWG file exists in the database.
    """

    md5sum = md5(content).hexdigest()  # Generate hash.

    # Check if generated hash already exists.
    if Dwg.objects.filter(md5=md5sum):
        return True
    return False


# Convert filename to AAAAA.ext
# Name uppercase and extension lowercase
def check_filename(filename):
    name = filename.split('.')[0].upper()
    ext = filename.split('.')[1].lower()

    return name + '.' + ext