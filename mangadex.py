#! /usr/bin/python
# -*- encoding : utf-8 -*-
import requests
import threading
import os
import sys
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
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
    location = os.path.join(MANGA_FOLDER, title, chapter, name[len(name) - 1])
    dl_name = os.path.join(chapter, name[len(name) - 1])

    if not os.path.isfile(location):
        image = requests.get(url).content
        print('Downloading image', dl_name)
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
        content = requests.get(url, headers=HEADERS).json()

        # Easy access to important variables
        hash = content['hash']
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
            url = os.path.join(server, hash, page)
            threaded_downloader(url, chapter, title)
        # Without delay script skips chapters
        time.sleep(0.1)


# Gets the chapters from mangas json file
def getchapters(manga_id):
    try:
        url = 'https://mangadex.org/api/?id={}&type=manga'.format(manga_id)
        data = requests.get(url, headers=HEADERS).json()
    except ValueError:
        print('"{}" is not a valid ID, exiting script...'.format(manga_id))
        sys.exit()

    createfolder(MANGA_FOLDER)
    list = []
    downloaded_chapters = []

    for chapter in data['chapter']:
        # downloaded_chapters and ch_number make sure that no duplicate chapters are downloaded
        ch_number = data['chapter'][chapter].get('chapter')
        # Checks that there are no dublicate chapters from different translators
        if data['chapter'][chapter].get('lang_code') == 'gb' and ch_number not in downloaded_chapters:
            list.append(chapter)
            downloaded_chapters.append(ch_number)
    createfolder(os.path.join(MANGA_FOLDER, data['manga']['title']))
    list.reverse()
    getimages(list, data['manga']['title'])


# Takes the full URL to mangadex or just the manga id
def userinput():
    if len(sys.argv) > 1:
        mangaurl = sys.argv[1]
        if '/' not in mangaurl:
            return mangaurl
    else:
        mangaurl = input('Link to mangadex: ')
    return mangaurl.split('/')[4]


def main():
    getchapters(userinput())


if __name__ == "__main__":
    main()
