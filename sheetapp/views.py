from sheetapp import app
from flask import request, render_template, send_from_directory, url_for, redirect, session
from src.crawl_sheet import crawl_image, convert_to_pdf
from src.db_utility import *
import sys
import os

from config import *

@app.before_first_request
def initdb_command():
	if not os.path.isdir(img_folder):
		os.makedirs(img_folder)
	if not os.path.isdir(pdf_folder):
		os.makedirs(pdf_folder)
	exec_db('CREATE TABLE IF NOT EXISTS sheets(title TEXT, link TEXT, converted TEXT, pages REAL)')

def convert_needed(url, song_exist, song_title = None):
	if not song_exist:
		song_title = crawl_image(url)
		data_entry(song_title,url)
	elif song_exist and song_exist['converted']=='No':
		song_title = song_exist['title']

	return song_title

@app.route('/', methods=['GET','POST'])
def crawl_music_sheet():

	if request.method == 'POST':
		url = request.form['crawl_url']
		session['url'] = url

		invalidate_metadata()
		song_existence = check_link(url)
		song_title = convert_needed(url, song_existence)

		if song_title:
			pages = convert_to_pdf(song_title)
			update_db(song_title, pages)
			
		return redirect(url_for('result'))

	return render_template('index.html')

@app.route('/finished', methods=['GET','POST'])
def result():

	song_info = check_link(session.get('url'))
	session['title'] = song_info['title']

	if request.method == 'POST':
		if request.form['download_or_crawl'] == 'Download PDF':
			return redirect(url_for('download_pdf'))
		else:
			return redirect(url_for('crawl_music_sheet'))

	return render_template('result.html', song_title = song_info['title'], pages = song_info['pages'])

@app.route('/pdf')
def download_pdf():
	song_title = session.get('title')
	return send_from_directory(directory = pdf_folder, filename = song_title+'.pdf')


	
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

