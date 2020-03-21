import os
import sys

import xbmc
import xbmcaddon

PY3 = sys.version_info.major >= 3
ADDON_ID = "plugin.image.pdfreader"
ADDON = xbmcaddon.Addon(ADDON_ID)
ADDON_NAME = ADDON.getAddonInfo("name")

get_setting = ADDON.getSetting
set_setting = ADDON.setSetting
open_settings = ADDON.openSettings

if PY3:
    translate = ADDON.getLocalizedString

    def str_to_bytes(s):
        return s.encode()

    def bytes_to_str(b):
        return b.decode()

    def str_to_unicode(s):
        return s
else:
    def translate(*args, **kwargs):
        return ADDON.getLocalizedString(*args, **kwargs).encode("utf-8")

    def str_to_bytes(s):
        return s

    def bytes_to_str(b):
        return b

    def str_to_unicode(s):
        return s.decode("utf-8")


ADDON_PATH = str_to_unicode(xbmc.translatePath(ADDON.getAddonInfo("path")))
DATA_PATH = str_to_unicode(xbmc.translatePath(ADDON.getAddonInfo("profile")))
IMG_FOLDER = os.path.join(ADDON_PATH, "resources", "img")


def get_local_folder():
    return get_setting("local-folder")


def check_picture_size():
    return get_setting("limite") == "true"


def show_real_thumbnails():
    return get_setting("thumbs") == "true"


def always_refresh_thumbnails():
    return get_setting("thumbs2") == "1"


def save_pdf():
    return get_setting("local") == "true"
