# -*- coding: UTF-8 -*-

import os
import sys
import json
import xbmc
import zlib
import utils
import base64
import urllib
import xbmcgui
import thumbnails
import xbmcplugin
from pdflib import pdf
from dialog_insert import DialogInsert


def add_page(name, path, thumbnail):
    list_item = xbmcgui.ListItem(name, iconImage="DefaultImage.png", thumbnailImage=thumbnail)
    list_item.setProperty("fanart_image", os.path.join(utils.IMG_FOLDER, "black-background.jpg"))
    list_item.setInfo(type="image", infoLabels={"Title": name})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=list_item)


def play_images(data):
    i = 1
    for img in data["images"]:
        if not utils.show_real_thumbnails():
            add_page("%s %d" % (utils.translate(30017), i), img, thumbnails.get_thumbnail(str(i)))
        else:
            add_page("%s %d" % (utils.translate(30017), i), img, img)

        i = 1 if i == 100 else i + 1

    xbmc.executebuiltin("Container.SetViewMode(500)")


def add_dir(label, url, thumbnail=None, folder=False, total=1):
    list_item = xbmcgui.ListItem(label, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
    list_item.setProperty('fanart_image', os.path.join(utils.IMG_FOLDER, "black-background.jpg"))
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=folder,
                                       totalItems=total)


def default():
    # Open PDF
    add_dir(utils.translate(30000), "plugin://%s/open_pdf" % utils.ADDON_ID,
            os.path.join(utils.IMG_FOLDER, "open.png"))

    # Open Settings
    add_dir(utils.translate(30001), "plugin://%s/open_settings" % utils.ADDON_ID,
            os.path.join(utils.IMG_FOLDER, "settings.png"))


def open_pdf():
    w = DialogInsert("plugin.image.pdfreader-dialog-insert.xml", utils.ADDON_PATH)
    w.doModal()
    if w.type != 0 and w.ret_val:
        pdf.play_pdf(w.ret_val)


def run():
    params = sys.argv[0].split("/")[3:]
    for index, param in enumerate(params):
        params[index] = urllib.unquote_plus(param)

    if len(params) > 1 and params[0] == "play_images":
        data = json.loads(params[1])
        play_images(data)
    elif len(params) > 1 and params[0] == "play_images_z":
        data = json.loads(zlib.decompress(base64.b64decode(params[1])))
        play_images(data)
    elif len(params) > 0 and params[0] == "open_pdf":
        open_pdf()
    elif len(params) > 0 and params[0] == "open_settings":
        utils.open_settings()
    else:
        default()

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=True)
