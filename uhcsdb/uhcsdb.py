# all the imports
import os
import sys
from os.path import abspath, dirname, join

import pybtex.database
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, g, redirect, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.middleware.proxy_fix import ProxyFix

from uhcsdb import features
from .models import Base, Micrograph

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

# Flask app configuration
# DATADIR = '/Users/brian/Research/projects/uhcs'
SQLALCHEMY_DATABASE_URI = 'uhcsdb/microstructures.sqlite'
MICROGRAPH_PATH = 'static/micrographs'
UPLOAD_FOLDER = join('uhcsdb', MICROGRAPH_PATH)
EXTRACT_PATH = join('static', 'pdf_stage')
PDF_STAGE = join('uhcsdb', EXTRACT_PATH)
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tif'}


def load_secret_key():
    pardir = os.path.dirname(__file__)
    keyfile = os.path.join(pardir, 'secret_key')
    with open(keyfile, 'rb') as f:
        return f.read()


app.config.update(dict(
    DATABASE=SQLALCHEMY_DATABASE_URI,
    MICROGRAPH_PATH=MICROGRAPH_PATH,
    DEBUG=False,
    SECRET_KEY=load_secret_key(),
))

app.config.from_envvar('UHCSDB_SETTINGS', silent=True)

_cwd = dirname(abspath(__file__))


@app.before_first_request
def build_search_tree():
    features.build_search_tree('uhcsdb/static/representations',
                               featurename='vgg16_multiscale_block5_conv3-vlad-32.h5'
                               )
    # features.build_search_tree(app.config['DATADIR'])


def connect_db(dbpath):
    engine = create_engine('sqlite:///' + dbpath)
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    db = db_session()
    return db


def get_db():
    if not hasattr(g, '_database'):
        g._database = connect_db(app.config['DATABASE'])
    return g._database


def paginate(results, page, per_page):
    start = (page - 1) * per_page
    if start < 0 or start > len(results):
        return []
    end = min(start + per_page, len(results))

    page_data = {'prev_num': page - 1, 'next_num': page + 1,
                 'has_prev': True, 'has_next': True}
    if page_data['prev_num'] <= 0:
        page_data['has_prev'] = False
    if end >= len(results):
        page_data['has_next'] = False

    return results[start:end], page_data


ENTRIES_PER_PAGE = 24


@app.route('/')
@app.route('/index')
@app.route('/entries/')  # , defaults={'page': 1})
@app.route('/entries/<int:page>')
def entries(page=1):
    # only show micrographs with these class labels
    unique_labels = {
        'spheroidite', 'spheroidite+widmanstatten', 'martensite', 'network',
        'pearlite', 'pearlite+spheroidite', 'pearlite+widmanstatten'
    }
    db = get_db()
    q = (db.query(Micrograph)
         .filter(Micrograph.primary_microconstituent.in_(unique_labels))
         )
    page_results, page_data = paginate(q.all(), page, ENTRIES_PER_PAGE)
    page_entries = [entry.info() for entry in page_results]

    return render_template('show_entries.html', entries=page_entries, pg=page_data)


@app.route('/micrograph/<int:entry_id>')
def show_entry(entry_id):
    db = get_db()
    entry = db.query(Micrograph).filter(Micrograph.micrograph_id == entry_id).first()
    return render_template('show_entry.html', entry=entry.info(), author=entry.contributor.info())


@app.route('/visual_query/<int:entry_id>')
def visual_query(entry_id):
    db = get_db()
    query = db.query(Micrograph).filter(Micrograph.micrograph_id == entry_id).first()
    author = query.contributor
    scores, nearest = features.query(entry_id)
    # write a single query and sort results on feature-space distance after
    # entries = db.query(Micrograph).filter(Micrograph.id.in_(nearest)).all()
    # write an individual query for each result -- won't scale
    micrographs = map(db.query(Micrograph).get, nearest)
    results = [micrograph.info() for micrograph in micrographs]
    results = zip(results, scores)
    return render_template('query_results.html', query=query.info(),
                           author=author.info(), results=results)


@app.route('/visualize')
def bokeh_plot():
    # bokeh_script=autoload_server(None,app_path="/visualize", url="http://rsfern.materials.cmu.edu")
    # session = pull_session(url="http://localhost:5006/visualize")
    # bokeh_script = server_session(None, session.id, url="http://localhost:5006/visualize")
    # return render_template('visualize.html', bokeh_script=bokeh_script)
    return render_template('visualize.html')


@app.route('/writeup')
def writeup():
    return redirect('https://arxiv.org/abs/1702.01117')


def format_bib_entry(entry):
    return entry
    # return markup


def author_list(entry):
    authors = [' '.join(p.last_names) for p in entry.persons['author']]
    firstauthors, lastauthor = authors[:-1], authors[-1]
    alist = ', '.join(firstauthors)
    alist += ', and {}'.format(lastauthor)
    return alist


def load_publication_data(path):
    """ use pybtex to display relevant publications """
    pub_db = pybtex.database.parse_file(path)

    publication_data = []
    for key, entry in pub_db.entries.items():
        pub = dict(entry.fields)
        pub['authors'] = author_list(entry)
        publication_data.append(pub)

    return publication_data


@app.route('/publications')
def publications():
    documentation = load_publication_data('uhcsdb/static/documentation.bib')
    sources = load_publication_data('uhcsdb/static/sources.bib')
    publication_data = load_publication_data('uhcsdb/static/publications.bib')
    return render_template('publications.html',
                           documentation=documentation,
                           sources=sources,
                           publications=publication_data)


if __name__ == '__main__':
    # features.build_search_tree('uhcsdb/static/representations',
    #                            featurename='vgg16_multiscale_block5_conv3-vlad-32.h5')
    app.config.from_object('config')

    with app.app_context():
        app.run(debug=False)
