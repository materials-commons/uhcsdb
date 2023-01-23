#BOKEH_LOG_LEVEL=debug bokeh serve --port 8010 --host=rsfern.materials.cmu.edu --allow-websocket-origin=uhcsdb.materials.cmu.edu --log-level=debug visualize.py

gunicorn --bind 127.0.0.1:9000 uhcsdb:app


