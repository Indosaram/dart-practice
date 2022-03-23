"""Common utils"""

import os
import zipfile
from xml.etree import ElementTree

import pandas as pd
import requests


def load_env(path: str = ".env"):
    with open(path, "r") as file:
        for row in file.readlines():
            key, value = row.split("=")
            os.environ[key] = value


def save_corp_list_as_cache() -> None:
    url = "https://opendart.fss.or.kr/api/corpCode.xml"
    params = {'crtfc_key': os.environ["DART_API_KEY"]}
    cache_dir = 'cache'

    response = requests.get(url, params=params)

    # save zip file and unzip
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    id_zip_path = os.path.join(os.getcwd(), cache_dir, 'id.zip')
    with open(id_zip_path, 'wb') as fp:
        fp.write(response.content)

    zf = zipfile.ZipFile(id_zip_path)
    zf.extractall(os.path.join(os.getcwd(), cache_dir))

    # parse xml
    xml_path = os.path.join(os.getcwd(), cache_dir, 'CORPCODE.xml')
    tree = ElementTree.parse(xml_path)
    root = tree.getroot()
    tags_list = root.findall('list')
    tags_list_dict = list(
        map(
            lambda tag: {child.tag: child.text for child in list(tag)},
            tags_list,
        )
    )
    df = pd.DataFrame(tags_list_dict)

    df.to_csv(os.path.join(cache_dir, 'corp_list.csv'))

    # cleanup
    os.remove(id_zip_path)
    os.remove(xml_path)


def find_corp_code_by_name(corp_name: str) -> str:
    corp_list = pd.read_csv(os.path.join('cache', 'corp_list.csv'))
    result = corp_list[corp_list["corp_name"].str.contains(corp_name)]
    corp_code = result.corp_code.iloc[0]

    return f"{corp_code:08d}"

