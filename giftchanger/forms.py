from django import forms
import PIL
from .models import Gift
import requests
import json
import random


class ImageFormRequired(forms.Form):
    image = forms.ImageField()


class ImageFormElective(forms.Form):
    image = forms.ImageField(required=False)


class NoImageForm(forms.Form):
    pass


def imgur_uploader(image_file, name="image", content_type=None):
    endpoint = "https://api.imgur.com/3/image"
    client_ids = "2bf2542859d3f52", "3546e87c0ba5843", "7d12b6e8542631c"
    client_id = "Client-ID " + random.choice(client_ids)

    files = {'image': (name, image_file, content_type)}
    headers = {"Authorization": client_id}

    res = requests.post(endpoint, headers=headers, files=files)
    res_dict = json.loads(res.text)

    if res_dict["success"]:
        link = res_dict["data"]["link"]
        return link

    else:
        return res_dict

