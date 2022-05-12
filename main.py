import requests
from pprint import pprint
import pathlib
from pathlib import Path
import os

VK_USER_ID = "552934290"

with open('vk_token.txt', 'r') as file_object:
    token = file_object.read().strip()


def get_vk_photo():
    params = {
        'owner_id': "552934290",
        'access_token': token,
        'v': '5.131',
        'album_id': 'profile',
        'extended': '1',
        'count': 5
    }
    response = requests.get(
        'https://api.vk.com/method/photos.get', params)
    # pprint(response.json())
    return response.json()


def sort_photos():
    data = get_vk_photo()
    for files in data['response']['items']:
        files_url = files['sizes'][-1]['url']
        file_name = files['likes']['count']
        images = requests.get(files_url)
        # pprint(sorted_files)

        with open("image %s" % file_name, 'wb') as file:
            file.write(images.content)


path = Path(pathlib.Path.cwd(), 'image 17')


class YaUploader:
    host = r'https://cloud-api.yandex.net'

    def __init__(self, token: str):
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
        # folder = self.create_folder()
        response = requests.put(upload_link, data=open(
            file_name, 'rb'), headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print('Success')


if __name__ == '__main__':
    sort_photos()
    with open('ya_token.txt', 'r') as file_object:
        token = file_object.read().strip()
        uploader = YaUploader(token)
        uploader.create_folder()
        result = uploader.upload_file('/backupfolder/image 17', path)
