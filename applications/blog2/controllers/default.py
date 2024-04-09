# -*- coding: utf-8 -*-
def index():
    # Pobierz tylko 3 najnowsze posty
    latest_images = db().select(db.image.ALL, orderby=db.image.date, limitby=(0, 3))

    # Pobierz posty według kategorii
    news_posts = db((db.image.id == db.image_category.image_id) &
                    (db.image_category.category_id == db.category.id) &
                    (db.category.name == 'Aktualności')).select(db.image.ALL, orderby=db.image.date)
    model_posts = db((db.image.id == db.image_category.image_id) &
                     (db.image_category.category_id == db.category.id) &
                     (db.category.name == 'Modele')).select(db.image.ALL, orderby=db.image.date)
    advice_posts = db((db.image.id == db.image_category.image_id) &
                      (db.image_category.category_id == db.category.id) &
                      (db.category.name == 'Porady')).select(db.image.ALL, orderby=db.image.date)
    traffic_regulations_posts = db((db.image.id == db.image_category.image_id) &
                                   (db.image_category.category_id == db.category.id) &
                                   (db.category.name == 'Przepisy drogowe')).select(db.image.ALL, orderby=db.image.date)

    return dict(latest_images=latest_images, news_posts=news_posts, model_posts=model_posts,
                advice_posts=advice_posts, traffic_regulations_posts=traffic_regulations_posts)


from gluon.tools import prettydate

@auth.requires_login()
def show():
    image = db.image(request.args(0, cast=int)) or redirect(URL('index'))
    db.post.image_id.default = image.id
    body = db.image()  # Dodanie pobrania treści body
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

    # Formatowanie daty komentarza za pomocą funkcji prettydate
    for comment in comments:
        comment.date = prettydate(comment.date)

    # Przekazujemy dane do widoku
    return dict(image=image, comments=comments, form=form, car_title=car_title, equipment=equipment, body=body)

def download():
    return response.download(request, db)

def user():
    return dict(form=auth())

@auth.requires_login()
def add_post():
    form = SQLFORM(db.image)
    try:
        if form.process().accepted:
            response.flash = 'Twój post został dodany'
            redirect(URL('index'))  # Przekierowanie po dodaniu posta
    except Exception as e:
        response.flash = 'Wystąpił błąd podczas przetwarzania formularza: {}'.format(e)

    return dict(form=form)

@auth.requires_login()
def assign_categories():
    # Pobierz wszystkie dostępne kategorie
    categories = db(db.category).select()

    # Pobierz wszystkie dostępne posty
    images = db().select(db.image.ALL, orderby=db.image.title)

    # Utwórz formularz do przypisywania kategorii
    form = FORM(
        *[
            DIV(
                LABEL(INPUT(_type='checkbox', _name='category_id', _value=category.id), category.name),
                _class='checkbox'
            ) for category in categories
        ],
        BR(),
        LABEL('Wybierz post/zdjęcie:', _for='image_id'),
        SELECT(
            *[OPTION(image.title, _value=image.id) for image in images],
            _name='image_id', _id='image_id',
            requires=IS_IN_DB(db, db.image.id, '%(title)s')
        ),
        BR(),
        INPUT(_type='submit', _value='Przypisz kategorie'),
        _method='post', _action=URL('default', 'assign_categories')
    )

    if form.accepts(request.post_vars, session):
        # Pobierz zaznaczone kategorie i image_id
        selected_categories = request.post_vars.getlist('category_id')
        image_id = request.post_vars.get('image_id')

        # Sprawdź, czy wybrane kategorie i image_id istnieją
        if selected_categories and image_id:
            # Iteruj przez zaznaczone kategorie
            for cat_id in selected_categories:
                # Sprawdź, czy dane przypisanie kategorii nie istnieje już dla danego posta
                existing_record = db((db.image_category.image_id == image_id) &
                                     (db.image_category.category_id == cat_id)).select().first()
                if not existing_record:
                    # Dodaj przypisanie kategorii do bazy danych dla konkretnego posta, jeśli nie istnieje jeszcze taki rekord
                    db.image_category.insert(image_id=image_id, category_id=cat_id)
                else:
                    # W przypadku istnienia już takiego rekordu, poinformuj użytkownika
                    response.flash = f'Kategoria "{existing_record.category_id.name}" jest już przypisana do tego posta'
                    break
            else:
                response.flash = 'Kategorie zostały przypisane'
                redirect(URL('index'))  # Przekierowanie po przypisaniu kategorii
        else:
            response.flash = 'Wybierz przynajmniej jedną kategorię i post/zdjęcie'

    return dict(form=form)

@auth.requires_login()
def add_equipment():
    # Pobierz wszystkie dostępne rodzaje wyposażenia
    equipment_records = db(db.equipment).select()

    # Utwórz checkboxy dla każdego rodzaju wyposażenia wraz z etykietami
    checkboxes = [DIV(
        LABEL(INPUT(_type='checkbox', _name='equipment_id', _value=equipment.id), equipment.name),
        _class='checkbox'
    )
        for equipment in equipment_records]

    # Utwórz listę rozwijaną z dostępnymi image_id
    image_options = [OPTION(image.title, _value=image.id) for image in db(db.image).select()]
    image_select = SELECT(image_options, _name='image_id', _id='image_id',
                          requires=IS_IN_DB(db, db.image.id, '%(title)s'))

    # Utwórz formularz zawierający checkboxy i listę rozwijaną
    form = FORM(
        *checkboxes,
        BR(),
        LABEL('Wybierz post/zdjęcie:', _for='image_id'),
        image_select,
        BR(),
        INPUT(_type='submit', _value='Dodaj wyposażenie'),
        _method='post', _action=URL('default', 'add_equipment')
    )

    if form.accepts(request.post_vars, session):
        # Pobierz zaznaczone wyposażenie i image_id
        selected_equipment = request.post_vars.getlist('equipment_id')
        image_id = request.post_vars.get('image_id')

        # Sprawdź, czy wybrane wyposażenie istnieje
        if selected_equipment and image_id:
            # Iteruj przez zaznaczone wyposażenie
            for eq_id in selected_equipment:
                # Sprawdź, czy dane wyposażenie nie jest już dodane do danego pojazdu
                existing_record = db((db.equipment_model.equipment_id == eq_id) & (
                            db.equipment_model.image_id == image_id)).select().first()
                if not existing_record:
                    # Dodaj wyposażenie do bazy danych dla konkretnego pojazdu, jeśli nie istnieje jeszcze taki rekord
                    db.equipment_model.insert(equipment_id=eq_id, image_id=image_id)
                else:
                    # W przypadku istnienia już takiego rekordu, poinformuj użytkownika
                    response.flash = f'Wyposażenie "{existing_record.equipment_id.name}" jest już dodane do tego pojazdu'
                    break
            else:
                response.flash = 'Wyposażenie zostało dodane'
                redirect(URL('index'))  # Przekierowanie po dodaniu wyposażenia
        else:
            response.flash = 'Wybierz przynajmniej jedno wyposażenie i post/zdjęcie'

    return dict(form=form)

@auth.requires_membership('manager')
def manage():
    grid = SQLFORM.smartgrid(db.image,linked_tables=['post'])
    grid_equipment = SQLFORM.smartgrid(db.equipment)
    grid_equipment_model = SQLFORM.smartgrid(db.equipment_model)
    return dict(grid=grid, grid_equipment=grid_equipment, grid_equipment_model=grid_equipment_model)
