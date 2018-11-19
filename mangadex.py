#! /usr/bin/python
# -*- encoding : utf-8 -*-
import requests
import threading
import os


# Starts threaded download
def threaded_downloader(url, chapter, manga):
    download_thread = threading.Thread(target=download, args=(url, chapter, manga))
    download_thread.start()


# Downloads file in format */manga/chapter/A1.png
def download(url, chapter, manga):
    name = url.split('/')
    location = os.path.join(manga, chapter, name[len(name) - 1])
    dl_name = os.path.join(chapter, name[len(name) - 1])

    if not os.path.isfile(location):
        image = requests.get(url).content
        print('Downloading image', dl_name)
        with open(location, 'wb') as file:
            file.write(image)
    else:
        print(dl_name, 'exists already')


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
        try:
            url = 'https://mangadex.org/api/?id=' + str(id) + '&type=chapter'
            content = requests.get(url).json()
        except ValueError:
            print(id, 'broke')
            pass

        # Easy access to important variables
        hash = content['hash']
        pages = content['page_array']
        chapter = content['chapter']
        server = content['server']

        # Fixes the server url
        if server == '/data/':
            server = 'https://mangadex.org/data/'
        if not chapter:
            chapter = str(0)

        # Starts the download process
        location = os.path.join(manga, chapter)
        createfolder(location)
        for page in pages:
            url = server + hash + '/' + page
            threaded_downloader(url, chapter, manga)


# Gets the chapters from mangas json file
def getchapters(manga):
    url = 'https://mangadex.org/api/?id=' + manga + '&type=manga'
    file = requests.get(url).json()

    list = []
    chapter_number = []

    for chapter in file['chapter']:
        number = file['chapter'][chapter].get('chapter')
        if file['chapter'][chapter].get('lang_code') == 'gb' and number not in chapter_number:
            list.append(chapter)
    createfolder(manga)
    getimages(list, manga)


def main():
    mangaurl = input('Link to mangadex: ')
    mangasplit = mangaurl.split('/')
    getchapters(mangasplit[4])


if __name__ == "__main__":
    main()
