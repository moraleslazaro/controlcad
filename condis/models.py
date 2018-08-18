from django.db import models


class Equip(models.Model):
    """
    Equips loaded from MSSQL Server.
    """
    codequipo = models.CharField(max_length=20, unique=True, primary_key=True)
    codfamilia = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=60)
    codmodelo = models.CharField(max_length=20)
    nota = models.CharField(max_length=50)
    CodComercial = models.CharField(max_length=25, null=True)

    def __unicode__(self):
        return u"%s - %s" % (self.codequipo, self.codfamilia)

    class Meta:
        ordering = ('codequipo',)
        db_table = 'equipos'
