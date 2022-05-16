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
    """
    Class to operate with VK API
    """

    host = r'https://api.vk.com'

    def __init__(self, token: str):
        with open('vk_token.txt', 'r') as file_object:
            token = file_object.read().strip()
        self.token = token

    def create_folder(self):
        """
        Method to create local folder to save downloaded files
        """
        path = os.getcwd()
        new_folder = path + '/images'
        try:
            os.mkdir((new_folder))
        except OSError:
            print(f'Unable to create folder :{new_folder}')
        else:
            print('folder successfully created')

    def get_vk_photo(self):
        '''
        Method to download profile photos from VK using VK API and to sort them 
        in json file depending on their size
        '''
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
            url, params).json()
        # pprint(response)
        self.json_to_save = []
        # Creating dict on files with identical number of likes
        data_on_files = {}
        for files in response['response']['items']:
            if files['likes']['count'] in data_on_files:
                data_on_files[files['likes']['count']] += 1
            else:
                data_on_files[files['likes']['count']] = 1

        # Defining the largest photos
        for files in response['response']['items']:
            file_params = sorted(
                files['sizes'], key=lambda x: x['height'] + x['width'], reverse=True)[0]

            # Creating the name for the photo
            if data_on_files.get(files['likes']['count'], 0) > 1:
                file_params['file_name'] = str(
                    files['likes']['count']) + '_' + str(files['date']) + '.jpg'
            else:
                file_params['file_name'] = str(
                    files['likes']['count']) + '.jpg'

            # Appending to resulting list (json_to_save)
            self.json_to_save.append(file_params)
        pprint(self.json_to_save)

        self.create_folder()
        """Downloading files into pre-created local folder"""
        for file in self.json_to_save:
            file_name = file.get('file_name')
            url = file.get('url')
            # Initializing progress bar
            bar = PixelBar('Processing', max=100)
            for i in range(100):
                time.sleep(0.001)
                bar.next()
            images = requests.get(url)
            with open(f'images/{file_name}', 'wb') as file:
                file.write(images.content)
                bar.finish()
        # Saving json info on selected files to our local folder
        with open('data.json', 'w') as write_file:
            json.dump(self.json_to_save, write_file, indent=4)

        return self.json_to_save


class YaUploader(VkDownloader):
    """
    Class to operate with Yandex API
    """
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
        # pprint(response.json())
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
        self.get_vk_photo()
        for i in self.json_to_save:
            file_name = i.get('file_name')
            url = i.get('url')
            self.upload_file(f'/backupfolder/{file_name}', url)


if __name__ == '__main__':
    downloader = VkDownloader(Token)
    downloader.get_vk_photo()
    uploader = YaUploader(Token)
    uploader.create_folder()
    result = uploader.save_file()
