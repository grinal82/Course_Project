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
            'owner_id': VK_USER_ID,
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

        # pprint(self.json_to_save)
        self.create_folder()
        """Downloading files into pre-created local folder
        """
        for file in self.json_to_save:
            file_name = file.get('file_name')
            url = file.get('url')
            # Initializing progress bar
            bar = PixelBar('Processing', max=100)
            for i in range(100):
                time.sleep(0.01)
                bar.next()
            images = requests.get(url)
            with open(f'images/{file_name}', 'wb') as file:
                file.write(images.content)
                bar.finish()

        # Saving json info on selected files to our local folder
        with open('data.json', 'w') as write_file:
            json.dump(self.json_to_save, write_file, indent=4)


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

    def create_folder(self):
        host = self.host
        self.path = f'/images'
        url = f"{host}/v1/disk/resources"
        headers = self.get_headers()
        params = {'path': self.path}
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 201:
            print('Folder created successfully')

    def upload_file(self):
        '''uploading files by their url taken from previously saved json file 
        using requests.post method
        '''
        host = self.host
        self.create_folder()
        with open('data.json') as f:
            data = json.load(f)
            for i in data:
                file_name = i.get('file_name')
                link = i.get('url')
                path = f'{host}/v1/disk/resources/upload'
                disc_path = f'/images/{file_name}'
                headers = self.get_headers()
                params = {'path': disc_path, 'url': link}
                response = requests.post(
                    url=path, headers=headers, params=params)
                if response.status_code == 202:
                    print('Uploaded successfully')
                else:
                    return {'code': response.status_code, 'text': response.text}


if __name__ == '__main__':
    downloader = VkDownloader(Token)
    downloader.get_vk_photo()
    uploader = YaUploader(Token)
    result = uploader.upload_file()
