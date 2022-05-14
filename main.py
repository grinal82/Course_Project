from tokenize import Token
import requests
from pprint import pprint
import pathlib
from pathlib import Path
from progress.bar import PixelBar
import time

VK_USER_ID = "552934290"
NUMBER_OF_PHOTOS = 5


class VkDownloader:
    host = r'https://api.vk.com'

    def __init__(self, token: str):
        with open('vk_token.txt', 'r') as file_object:
            token = file_object.read().strip()
        self.token = token

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
        # pprint(response.json())
        return response.json()

    def sort_photos(self):
        data = self.get_vk_photo()
        for files in data['response']['items']:
            files_url = files['sizes'][-1]['url']
            file_name = files['likes']['count']
            bar = PixelBar('Processing', max=100)
            for i in range(100):
                time.sleep(0.001)
                bar.next()
            bar.finish()
            images = requests.get(files_url)
            # pprint(sorted_files)

            with open("image %s" % file_name, 'wb') as file:
                file.write(images.content)


path = Path(pathlib.Path.cwd(), 'image 17')


class YaUploader:
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

    def upload_file(self, path, file_name):
        upload_link = self._get_upload_link(path)
        headers = self.get_headers()
        response = requests.put(upload_link, data=open(
            file_name, 'rb'), headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print('Successful Upload')


if __name__ == '__main__':
    downloader = VkDownloader(Token)
    downloader.sort_photos()
    uploader = YaUploader(Token)
    uploader.create_folder()
    result = uploader.upload_file('/backupfolder/image 17', path)
