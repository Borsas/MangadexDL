#! /usr/bin/python
# -*- encoding : utf-8 -*-
import requests
import threading
import os
import sys
import time
import cfscrape


HEADERS = {"User-Agent": "Mozilla/5.0"}
scraper = cfscrape.create_scraper()

# Allows user to change save destination
if len(sys.argv) == 3:
    MANGA_FOLDER = sys.argv[2]
else:
    MANGA_FOLDER = 'manga'


# Starts threaded download
def threaded_downloader(url, chapter, title):
    download_thread = threading.Thread(target=download, args=(url, chapter, title))
    download_thread.start()


# Downloads file in format */manga/chapter/A1.png
def download(url, chapter, title):
    name = url.split('/')
    location = os.path.join(MANGA_FOLDER, title, chapter, name[-1])

    if not os.path.isfile(location):
        image = requests.get(url).content
        print('Downloading image', location)
        with open(location, 'wb') as file:
            file.write(image)


# Creates folder
def createfolder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
        print('Created folder "{}"'.format(folder))
    else:
        print('"{}" exists already'.format(folder))


# Gets the images from chapters json file
def getimages(chapters, title):
    for id in chapters:
        url = 'https://mangadex.org/api/?id={}&type=chapter'.format(str(id))
        try:
            content = requests.get(url, headers=HEADERS).json()
        except ValueError:
            content = scraper.get(url).json()

        # Easy access to important variables
        manga_hash = content['hash']
        pages = content['page_array']
        chapter = content['chapter']
        server = content['server']

        # Fixes the server url
        if server == '/data/':
            server = 'https://mangadex.org/data/'
        if not chapter:
            chapter = '0'

        # Starts the download process
        location = os.path.join(MANGA_FOLDER, title, chapter)
        createfolder(location)
        for page in pages:
            url = os.path.join(server, manga_hash, page)
            threaded_downloader(url, chapter, title)
        # Without delay script skips chapters
        time.sleep(0.1)


# Gets the chapters from mangas json file
def getchapters(manga_id):
    url = 'https://mangadex.org/api/?id={}&type=manga'.format(manga_id)
    try:
        data = requests.get(url, headers=HEADERS).json()
    except ValueError:
        print('Mangadex is using Cloudflare DDOS protect, this will take a moment...')
        data = scraper.get(url).json()
        # sys.exit('"{}" is not a valid ID, exiting script...'.format(manga_id))
    chapters = []
    downloaded_chapters = []
    try:
        for chapter in data['chapter']:
            # downloaded_chapters and ch_number make sure that no duplicate chapters are downloaded
            ch_number = data['chapter'][chapter].get('chapter')
            # Checks that there are no dublicate chapters from different translators
            if data['chapter'][chapter].get('lang_code') == 'gb' and ch_number not in downloaded_chapters:
                chapters.append(chapter)
                downloaded_chapters.append(ch_number)
    except KeyError:
        sys.exit('"{}" is not a valid ID, exiting script...'.format(manga_id))

    createfolder(MANGA_FOLDER)
    createfolder(os.path.join(MANGA_FOLDER, data['manga']['title']))
    chapters.reverse()
    getimages(chapters, data['manga']['title'])


# Get the manga URL
def get_mangaurl(mangaurl):
    if '/' not in mangaurl:
            return mangaurl
    else:
        return mangaurl.split('/')[4]


# Takes the full URL to mangadex or just the manga id
def userinput():
    if len(sys.argv) > 1:
        return get_mangaurl(sys.argv[1])
    else:
        return get_mangaurl(input('Link to mangadex: '))


def main():
    getchapters(userinput())


if __name__ == "__main__":
    main()
