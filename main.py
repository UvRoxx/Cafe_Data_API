from flask import Flask, jsonify, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


def convert_db_to_dict(db_obj):
    d = {}
    for column in db_obj.__table__.columns:
        d[column.name] = str(getattr(db_obj, column.name))
    return d


## HTTP GET - Read Record
@app.route('/random', methods=['GET'])
def send_page():
    cafe_id = randint(1, 21)
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    d = {"cafe": convert_db_to_dict(cafe)}
    return jsonify(d)


@app.route("/all", methods=["GET"])
def send_all():
    cafes = db.session.query(Cafe).all()
    response = []
    for cafe in cafes:
        d = {"cafe": convert_db_to_dict(cafe)}
        response.append(d)
    return jsonify(response)


@app.route('/search', methods=['GET'])
def search_by_loc():
    loc = request.args.get('loc')
    try:
        cafe = Cafe.query.filter_by(location=loc).first()
        return jsonify({"cafe": convert_db_to_dict(cafe)})
    except AttributeError:
        return jsonify({"error_code": 404, "message": "resource not found invalid query"})


def get_bool(para):
    return bool(int(para))


## HTTP POST - Create Record

@app.route("/add", methods=['POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        map_url = request.form.get('map_url')
        location = request.form.get('location')
        seats = (request.form.get('seats'))
        has_toilet = get_bool(request.form.get('has_toilet'))
        has_wifi = get_bool(request.form.get('has_wifi'))
        has_sockets = get_bool(request.form.get('has_sockets'))
        can_take_calls = get_bool(request.form.get('can_take_calls'))
        coffee_price = request.form.get('coffee_price')
        img_url = request.form.get('img_url')

        new_cafe = Cafe(name=name, map_url=map_url, location=location, seats=seats, has_sockets=has_sockets,
                        has_toilet=has_toilet, has_wifi=has_wifi, can_take_calls=can_take_calls,
                        coffee_price=coffee_price, img_url=img_url)
        print("new cafe created success")
        db.session.add(new_cafe)
        db.session.commit()
        print("ADDED")
        return jsonify({"response": {"success": "successfully added the new cafe"}})


## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<id>", methods=['POST'])
def update_price(id):
    try:
        cafe_to_update = Cafe.query.get(id)
        cafe_to_update.coffee_price = request.form.get('price')
        db.session.commit()
        return jsonify({"success": "Price Updated Successfully"})
    except AttributeError:
        return jsonify({"error": {"Not Found": "Sorry the cafe id was not found in the database"}})


## HTTP DELETE - Delete Record

@app.route('/delete-cafe/<key>', methods=['POST'])
def delete(key):
    if key != "TopSecretKey":
        return jsonify({"error": "Invalid API Key"})
    else:
        id_to_del=request.form.get('id')
        try:
            cafe_to_del = Cafe.query.get(id_to_del)
            db.session.delete(cafe_to_del)
            db.session.commit()
            return jsonify({"success": "cafe deleted successfully"})
        except AttributeError:
            print(id_to_del)
            return jsonify({"error": "Id Not Found"})


if __name__ == '__main__':
    app.run(debug=True)
