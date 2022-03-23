import os
import zipfile

import pandas as pd
import requests


def get_receipt_no(corp_code: str, bgn_de: str, end_de: str) -> str:
    assert len(corp_code) == 8

    params = {
        'crtfc_key': os.environ["DART_API_KEY"],
        'corp_code': corp_code,
        'bgn_de': bgn_de,
        'end_de': end_de,
    }

    response = requests.get(
        "https://opendart.fss.or.kr/api/list.json", params=params
    )

    # TODO: check api response status
    # if response.status_code != 200:
    #     raise HTTPError

    data = response.json()
    df = pd.DataFrame(data.get('list'))[["report_nm", "rcept_no"]]
    df = df[
        df["report_nm"].str.contains("증권신고서")
        & df["report_nm"].str.contains("발행조건확정")
    ]
    return df["rcept_no"].iloc[0]


def get_document(rcept_no: str) -> pd.DataFrame:

    url = "https://opendart.fss.or.kr/api/document.xml"

    params = {'crtfc_key': os.environ["DART_API_KEY"], 'rcept_no': rcept_no}

    doc_zip_path = os.path.join('cache', 'document.zip')
    response = requests.get(url, params=params)
    with open(doc_zip_path, 'wb') as fp:
        fp.write(response.content)

    zf = zipfile.ZipFile(doc_zip_path)
    zipinfo = zf.infolist()
    filename = zipinfo[0].filename
    xml_data = zf.read(filename)

    xml_text = xml_data.decode('euc-kr')

    # cleaning bad encoded texts
    xml_text = xml_text.replace('&cr;', '&#13;')
    xml_text = xml_text.replace('<주', '&lt;주')
    xml_text = xml_text.replace('M&A', 'M&amp;A')
    xml_text = xml_text.replace('R&D', 'R&amp;D')

    os.remove(doc_zip_path)

    return pd.read_html(xml_text)
