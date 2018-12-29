#! /usr/bin/python
# -*- encoding : utf-8 -*-
import requests
import threading
import os
import time


# Starts threaded download
def threaded_downloader(url, chapter, manga):
    download_thread = threading.Thread(target=download, args=(url, chapter, manga))
    download_thread.start()


# Downloads file in format */manga/chapter/A1.png
def download(url, chapter, manga):
    name = url.split('/')
    location = os.path.join('manga', manga['title'], chapter, name[len(name) - 1])
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
        print('Created folder', folder)
    else:
        print(folder + ' exists already')


# Gets the images from chapters json file
def getimages(chapters, manga):
    for id in chapters:
        url = 'https://mangadex.org/api/?id=' + str(id) + '&type=chapter'
        content = requests.get(url).json()

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
        location = os.path.join('manga', manga['title'], chapter)
        createfolder(location)
        for page in pages:
            url = server + hash + '/' + page
            threaded_downloader(url, chapter, manga)
        # Without delay program skips chapters
        time.sleep(0.1)


# Gets the chapters from mangas json file
def getchapters(manga):
    url = 'https://mangadex.org/api/?id=' + manga['id'] + '&type=manga'
    file = requests.get(url).json()

    list = []
    chapter_numbers = []

    for chapter in file['chapter']:
        # chapter_numbers and ch_number make sure that no duplicate chapters are downloaded
        ch_number = file['chapter'][chapter].get('chapter')
        if file['chapter'][chapter].get('lang_code') == 'gb' and ch_number not in chapter_numbers:
            list.append(chapter)
            chapter_numbers.append(ch_number)
    createfolder(os.path.join('manga', manga['title']))
    list.reverse()
    getimages(list, manga)


def main():
    createfolder('manga')
    mangaurl = input('Link to mangadex: ')
    mangasplit = mangaurl.split('/')
    url = 'https://mangadex.org/api/?id=' + mangasplit[4] + '&type=manga'
    link = requests.get(url).json()
    manganame = {'id': mangasplit[4],
                 'title': link['manga']['title']}

    getchapters(manganame)


if __name__ == "__main__":
    main()
