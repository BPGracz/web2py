# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = []
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_stacked'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Łączenie z bazą danych
db = DAL("sqlite://storage.sqlite")

# -------------------------------------------------------------------------
# Importowanie narzędzi globalnych od tworzenia użytkownika

from gluon.tools import Auth
auth = Auth(db)
auth.define_tables(username=True)

# -------------------------------------------------------------------------

# Tworzenie modelu image - posty
db.define_table('image',
   Field('date', 'date', default=request.now, writable=False, readable=False),
   Field('title', label='Tytuł', unique=True),
   Field('body', 'text', label='Treść'),
   Field('file', 'upload', label='Plik'),
   format='%((title)s)'
)

# Tworzenie modelu kategorii
db.define_table('category',
   Field('name', unique=True),
   format='%((name)s)'
)


# Tworzenie tabeli łączącej image i category
db.define_table('image_category',
   Field('image_id', 'reference image'),
   Field('category_id', 'reference category')
)

# Ustalanie wymagań dla nowych pól dla image
db.image.title.requires = IS_NOT_IN_DB(db, db.image.title)
db.image.file.requires = IS_NOT_EMPTY()

# Ustalanie wymagań dla nowych pól dla category
db.category.name.requires = IS_NOT_IN_DB(db, db.category.name)

# -------------------------------------------------------------------------
# Tworzenie modelu post - komentarze
db.define_table('post',
   Field('date', 'datetime', default=request.now, writable=False, readable=False),
   Field('image_id', 'reference image'),
   Field('author', default=auth.user.username if auth.user else None, label='Autor:'),
   Field('body', 'text',  label='Komentarz')
)

# Ustalanie wymagań dla nowych pól dla post
db.post.image_id.requires = IS_IN_DB(db, db.image.id, '%(title)s')
db.post.author.requires = IS_NOT_EMPTY()
db.post.body.requires = IS_NOT_EMPTY()
db.post.image_id.writable = db.post.image_id.readable = False
db.post.author.writable = False

# -------------------------------------------------------------------------
# Tworzenie modelu equipment - wyposażenie aut
db.define_table('equipment',
    Field('name', unique=True),
    format='%(name)s')

# -------------------------------------------------------------------------
# Tabela łącząca
db.define_table('equipment_model',
    Field('equipment_id', 'reference equipment'),
    Field('image_id', 'reference image'),
)

# Ustalanie wymagań dla nowych pól dla tabeli łączącej equipment_model
db.equipment_model.equipment_id.requires = IS_IN_DB(db, db.equipment.id, '%(name)s')
db.equipment_model.image_id.requires = IS_IN_DB(db, db.image.id, '%(title)s')

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)