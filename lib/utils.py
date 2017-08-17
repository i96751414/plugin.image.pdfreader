# -*- coding: UTF-8 -*-

import os
import xbmc
import xbmcaddon

ADDON_ID = "plugin.image.pdfreader"
ADDON = xbmcaddon.Addon(ADDON_ID)
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo("path")).decode('utf-8')
ADDON_NAME = ADDON.getAddonInfo("name")
DATA_PATH = xbmc.translatePath(ADDON.getAddonInfo("profile")).decode("utf-8")
IMG_FOLDER = os.path.join(ADDON_PATH, "resources", "img")


def translate(text):
    return ADDON.getLocalizedString(text).encode("utf-8")


def get_setting(setting):
    return ADDON.getSetting(setting)


def set_setting(setting, value):
    ADDON.setSetting(setting, value=value)


def open_settings():
    ADDON.openSettings()


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
