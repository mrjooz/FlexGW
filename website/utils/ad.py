#!/usr/bin/env python
# coding=utf-8

import base64
import hmac
import urllib
from hashlib import sha1


def sign(params):
    paramsStr = ""
    for i, item in enumerate(params):
        paramsStr += item
        if i < len(params) - 1:
          paramsStr += "\n"

    h = hmac.new("staycloud", paramsStr, sha1)
    signStr = base64.encodestring(h.digest())
    signStr = signStr.replace("\\", "-")
    signStr = signStr.replace("/", "-")
    return urllib.quote(signStr[:-1])


def ad_url(loc, preview):
    params = {
        "res": 'zhuyun_flexgw',
        "loc": loc,
        "lan": 'chs',
        "sta": 'standard'
    }
    if preview:
        params['sta'] = 'preview'

    keyArr = ["res", "loc", "lan", "sta"]
    keyArr.sort()
    paramsVal = []
    for key in keyArr:
        paramsVal.append(params[key])

    signStr = sign(paramsVal)
    url = "http://ossupdate.jiagouyun.com/Interface/getNewAd/sta/%s/res/%s/loc/%s/lan/%s/sign/%s" % (params['sta'], params['res'], params['loc'], params['lan'], signStr)
    return url


def convert_ads(ads):
    ads_converted = []
    titles = ads['title'].split(",")
    descriptions = ads['description'].split(",")
    images = ads['image'].split(",")
    urls = ads['url'].split(",")
    titlecolors = ads['titlecolor'].split(",")
    bgcolors = ads['bgcolor'].split(",")
    endtimes = ads['endtime'].split(",")

    for i in range(len(images)):
        ad = {
            "title": __get_from_list(titles, i, ""),
            "description": __get_from_list(descriptions, i, ""),
            "image": __get_from_list(images, i, ""),
            "url": __get_from_list(urls, i, ""),
            "titlecolor": __get_from_list(titlecolors, i, "ffffff"),
            "bgcolor": __get_from_list(bgcolors, i, "ffffff"),
            "endtime": __get_from_list(endtimes, i, endtimes[0]),
        }
        ads_converted.append(ad)
    return ads_converted


def __get_from_list(_list, i, default):
    if i + 1 > len(_list):
        return default
    else:
        return _list[i]
