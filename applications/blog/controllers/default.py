def index():
    images = db().select(db.image.ALL, orderby=db.image.title)
    return dict(images=images)

@auth.requires_login()
def show():
    image = db.image(request.args(0, cast=int)) or redirect(URL('index'))
    db.post.image_id.default = image.id
    form = SQLFORM(db.post)
    if form.process().accepted:
        response.flash = 'Twój komentarz został umieszczony'
    comments = db(db.post.image_id == image.id).select()

    # Pobierz ID obrazu (image) dla danego auta na podstawie argumentu żądania
    image_id = request.args(0, cast=int)

    # Pobierz tytuł auta na podstawie jego ID
    car_title = db(db.image.id == image_id).select(db.image.title).first()

    # Pobierz przypisane wyposażenie tylko dla tego obrazu
    equipment = db(
        (db.equipment_model.image_id == image_id) & (db.equipment_model.equipment_id == db.equipment.id)).select(
        db.equipment.name)

    # Przekazujemy dane do widoku
    return dict(image=image, comments=comments, form=form, car_title=car_title, equipment=equipment)

def download():
    return response.download(request, db)

def user():
    return dict(form=auth())

@auth.requires_login()
def add_post():
    form = SQLFORM(db.image)
    if form.process().accepted:
        response.flash = 'Twój post został dodany'
        redirect(URL('index'))  # Przekierowanie po dodaniu posta
    return dict(form=form)

@auth.requires_login()
def add_equipment():
    form = SQLFORM(db.equipment_model)
    if form.process(onvalidation=check_equipment).accepted:
        response.flash = 'Wyposażenie zostało dodane'
        redirect(URL('index'))  # Przekierowanie po dodaniu wyposażenia
    return dict(form=form)

def check_equipment(form):
    # Sprawdź, czy dane wyposażenie już istnieje w bazie danych
    existing_equipment = db(
        (db.equipment_model.equipment_id == form.vars.equipment_id) &
        (db.equipment_model.image_id == form.vars.image_id)
    ).select()

    if existing_equipment:
        form.errors.equipment_id = 'To wyposażenie zostało już dodane do tego auta'

@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.image,linked_tables=['post'])
    grid_equipment = SQLFORM.smartgrid(db.equipment)
    grid_equipment_model = SQLFORM.smartgrid(db.equipment_model)
    return dict(grid=grid, grid_equipment=grid_equipment, grid_equipment_model=grid_equipment_model)
