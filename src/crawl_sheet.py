import multiprocessing
from multiprocessing.pool import ThreadPool
from itertools import repeat
from lxml import html
from PIL import Image
from fpdf import FPDF
import requests
import os
import io

from config import *

url = 'http://m.hqgq.com/qinpu/51610.html'

def get_img_url(url):
    resp = requests.get(url)
    response = html.fromstring(resp.text)
    img_urls = response.xpath('//div[@class="qupucont"]/img/@src')
    song_title = response.xpath('//h1/text()')[-1]
    return song_title, img_urls

def download_img(i,title_url):
    title, url = title_url
    img = requests.get(url)    
    image_file = io.BytesIO(img.content)
    Image.open(image_file).convert('RGB').save("{}/{}/page_{}.jpg".format(img_folder,title,i+1))

def crawl_image(url):
    pool = ThreadPool(multiprocessing.cpu_count())
    song_title, img_urls = get_img_url(url)
    os.mkdir('{}/{}'.format(img_folder, song_title))
    pool.starmap(download_img,enumerate(zip(repeat(song_title),img_urls)))
    pool.close() 
    pool.join()
    return song_title

def convert_to_pdf(song):
    pdf = FPDF()

    song_folder = os.path.join(img_folder,song)
    pg = 0
    for image in os.listdir(song_folder):
        pg += 1
        pdf.add_page()
        pdf.image(os.path.join(song_folder,image),0,0,210,297) #A4 is 210mm x 297mm

    pdf.output(os.path.join(pdf_folder,song+".pdf"), "F")
    return pg

if __name__=='__main__':
    song = crawl_image(url)
    convert_to_pdf(song)
    