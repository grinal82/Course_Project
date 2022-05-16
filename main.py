from tokenize import Token
import requests
from pprint import pprint
from progress.bar import PixelBar
import time
import os
import json

VK_USER_ID = "552934290"
NUMBER_OF_PHOTOS = 5


class VkDownloader:
    host = r'https://api.vk.com'

    def __init__(self, token: str):
        with open('vk_token.txt', 'r') as file_object:
            token = file_object.read().strip()
        self.token = token

    def create_folder(self):
        path = os.getcwd()
        new_folder = path + '/images'
        try:
            os.mkdir((new_folder))
        except OSError:
            print(f'Unable to create folder :{new_folder}')
        else:
            print('folder successfully created')

    def get_vk_photo(self):
        params = {
            'owner_id': "552934290",
            'access_token': self.token,
            'v': '5.131',
            'album_id': 'profile',
            'extended': '1',
            'count': NUMBER_OF_PHOTOS
        }
        url = f'{self.host}/method/photos.get'
        response = requests.get(
            url, params)
        pprint(response.json())
        return response.json()

    def sort_photos(self):
        new_folder = self.create_folder()
        data = self.get_vk_photo()
        self.json_to_save = []
        for files in data['response']['items']:
            data_on_file = {}
            data_on_file['file_name'] = files['likes']['count']
            data_on_file['size'] = files['sizes'][-1]['type']
            data_on_file['url'] = files['sizes'][-1]['url']
            self.json_to_save.append(data_on_file)
            files_url = files['sizes'][-1]['url']
            file_name = files['likes']['count']
            bar = PixelBar('Processing', max=100)
            for i in range(100):
                time.sleep(0.001)
                bar.next()
            bar.finish()
            self.images = requests.get(files_url)

            with open(f'images/{file_name}.jpeg', 'wb') as file:
                file.write(self.images.content)

            with open('data.json', 'w') as write_file:
                json.dump(self.json_to_save, write_file, indent=4)

        return self.json_to_save


class YaUploader(VkDownloader):
    host = r'https://cloud-api.yandex.net'

    def __init__(self, token: str):
        with open('ya_token.txt', 'r') as file_object:
            token = file_object.read().strip()
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def _get_upload_link(self, path):
        url = f'{self.host}/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {'path': path, 'overwrite': True}
        response = requests.get(url, params=params, headers=headers)
        pprint(response.json())
        return response.json().get('href')

    def create_folder(self):
        url = f"{self.host}/v1/disk/resources?path=backupfolder"
        headers = self.get_headers()
        response = requests.put(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print('Folder created successfully')

    def upload_file(self, path, url: str):
        upload_link = self._get_upload_link(path)
        headers = self.get_headers()
        params = {'path': path, 'url': url}
        response = requests.put(
            upload_link, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 201:
            print('Successful Upload')

    def save_file(self):
        self.sort_photos()
        for i in self.json_to_save:
            file_name = i.get('file_name')
            url = i.get('url')
            self.upload_file(f'/backupfolder/{file_name}.jpeg', url)


if __name__ == '__main__':
    downloader = VkDownloader(Token)
    downloader.sort_photos()
    # downloader.save_json()
    uploader = YaUploader(Token)
    # uploader.create_folder()
    result = uploader.save_file()
