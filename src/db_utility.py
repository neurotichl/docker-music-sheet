from PyPDF2 import PdfFileReader
from config import *
from flask import g
import sqlite3
import os

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect('musicsheet/musicsheets.db')
    db = g.sqlite_db
    db.row_factory = sqlite3.Row    
    return db

def query_db(query, args=()):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv

def exec_db(query, args=()):
	db = get_db()
	db.execute(query, args)
	db.commit()

def data_entry(title,link,status = 'No',pages=0):
	exec_db("INSERT INTO sheets(title, link, converted, pages) VALUES (?,?,?,?)", [title,link,status,pages])

def check_link(link):
    song = query_db('SELECT * FROM sheets WHERE link = ?',[link])
    return song[0] if song else None

def update_db(title, pages):
	exec_db("UPDATE sheets SET converted = 'Yes', pages = ? WHERE title = ?",[pages,title])

def invalidate_metadata():
	'''
	Check the database if it's up-to-date
	'''
	def check_status_pages(status,title, pages=0):
		s1 = 'No' if status == 'Yes' else 'Yes'
		exec_db("UPDATE sheets SET converted = CASE WHEN converted = ? THEN ? ELSE converted END, pages = ? WHERE title = ?",[s1,status,pages,title])

	def get_pdf_pages(title):
		return PdfFileReader(open('{}/{}.pdf'.format(pdf_folder,title),'rb')).getNumPages()

	def check_db(title, case):
		# print(title,case)
		if case in [3,7]:
			check_status_pages('Yes',title,get_pdf_pages(title))
		elif case == 5:
			check_status_pages('No',title)
		elif case == 6:
			data_entry(title, 'Unknown','Yes',len(os.listdir(os.path.join(img_folder,title))))
		elif case == 4:
			data_entry(title, 'Unknown','No')
		elif case == 2:
			data_entry(title, 'Unknown','Yes',get_pdf_pages(title))
		elif case == 1:
			exec_db("DELETE FROM sheets WHERE title = ?",[title])

	db_songlist = query_db("SELECT title FROM sheets")
	db_songlist = [s['title'] for s in db_songlist]
	img_songlist = os.listdir(img_folder)
	pdf_songlist = [i.replace('.pdf','') for i in os.listdir(pdf_folder)]

	for i in set(db_songlist).union(set(img_songlist), set(pdf_songlist)):
		check_db(i,4*(i in img_songlist) + 2*(i in pdf_songlist) + (i in db_songlist))
