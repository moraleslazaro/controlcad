# ControlCAD database routers
class MSSQLRouter(object):
    """
    A router to control all database operations on models in the
    condis application. This router is needed in order to get automatic
    database routing for condis application related queries. In this case
    only read access is needed.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read condis models go to bdfrioclima.
        """
        if model._meta.app_label == 'condis':
            return 'bdfrioclima'
        return None

    def db_for_write(self, model, **hints):
        """
        Write attempts are not allowed.
        """
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations are not allowed.
        """
        return None

    def allow_syncdb(self, db, model):
        """
        Syncdb operation are not allowed.
        """
        return None