from flask import Flask, request, render_template, jsonify, send_from_directory
import sqlite3
from flask import g
import json
import re
from flask_sitemap import Sitemap


app = Flask(__name__,static_folder='static')
ext = Sitemap(app=app)

# DATABASE INFO
DATABASE = 'legalEntityDB.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# MAIN page routes

@app.route('/')
def home():
    return render_template('index.html')

@ext.register_generator
def home():
    # Not needed if you set SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS=True
    yield 'home', {}

# MAIN page routes END

info = []


# SEARCH page routes
@app.route('/search', methods=['GET', 'POST'])
def searchPage():
    return render_template('search.html')


@app.route('/search/cards', methods=['GET', 'POST'])
def searchResult():
    return render_template('card.html', data=info)


@app.route('/search/cards/<entityId>', methods=['GET', 'POST'])
def getInfo(entityId):
    cursor = get_db().cursor()
    query = "SELECT division_name,division_type,division_email,division_phone,residence_addresses,division_id FROM pmg_legal_entity_divisions_info WHERE pmg_legal_entity_divisions_info.legal_entity_id LIKE '{}%'".format(
        entityId)
    cursor.execute(query)
    divisions = cursor.fetchall()
    # doctors = []
    # for row in divisions:
    #     marker = row[5]
    #     cursor = get_db().cursor()
    #     query = "SELECT employee_speciality,party_name FROM pmg_all_pmd_doctor_info WHERE pmg_all_pmd_doctor_info.division_id LIKE '{}%'".format(marker)
    #     cursor.execute(query)
    #     result = cursor.fetchall()
    #     doctors.append(result)
    return render_template('entity.html', divisions=divisions)


@app.route('/search/api/', methods=['GET', 'POST'])
def searchArea():
    searchbox = request.form.get('area')
    cursor = get_db().cursor()
    query = "SELECT registration_settlement FROM pmg_legal_entity_info WHERE registration_area LIKE '{}%' COLLATE utf8_general_ci ORDER BY registration_area ".format(
        searchbox)
    cursor.execute(query)
    result = cursor.fetchall()
    result = (list(set(result)))
    resultUpd = []
    for i in result:
        for a in i:
            a = str(a)
            resultUpd.append(a)
    resultUpd = sorted(resultUpd)
    return jsonify(resultUpd)


@app.route('/search/api/city/', methods=['GET', 'POST'])
def searchCity():
    searchBox = request.json['data']
    cursor = get_db().cursor()
    query = "SELECT legal_entity_id,legal_entity_name,legal_entity_email,legal_entity_phone,legal_entity_owner_name,registration_addresses FROM pmg_legal_entity_info WHERE registration_settlement LIKE '{}%' COLLATE utf8_general_ci ORDER BY registration_area".format(
        searchBox)
    cursor.execute(query)
    result = cursor.fetchall()
    global info
    info = result
    return jsonify(info)


# SEARCH page routes END

@app.route('/info', methods=['GET', 'POST'])
def newsPage():
    f = open('articles.json', )
    data = json.load(f)
    return render_template('info.html', data=data)
    f.close()

@app.route('/info/articles/<title>', methods=['GET', 'POST'])
def getArticle(title):
    f = open('articles.json', )
    data = json.load(f)
    TAG_RE = re.compile(r'<br>')
    for d in data:
        if title == d['articleTitle']:
            title = TAG_RE.sub('', title)
            image = d['articleImg']
            text = TAG_RE.sub('', d['articleText'][0])
            orig_url = d['articleUrl']
    return render_template('article.html', title=title, image=image, text=text, url=orig_url)
    f.close()



# SEO SECTION
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
