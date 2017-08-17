# -*- coding: UTF-8 -*-

import os
import utils
import xbmcgui
from dialog import *


class DialogInsert(xbmcgui.WindowXMLDialog):
    def __init__(self, xml_filename, script_path):
        xbmcgui.WindowXML.__init__(self, xml_filename, script_path)
        self.ret_val = ""
        self.type = 0
        # Control IDs
        self.close_button_id = 32500
        self.radio_button_1_id = 32501
        self.radio_button_2_id = 32502
        self.ok_button_id = 32508
        self.url_button_id = 32505
        self.path_button_id = 32507

    def onInit(self):
        self.set_option_1()

    def onClick(self, control_id):
        if control_id == self.close_button_id:
            self.cancelled()
        elif control_id == self.radio_button_1_id:
            self.set_option_1()
        elif control_id == self.radio_button_2_id:
            self.set_option_2()
        elif control_id == self.ok_button_id:
            self.ok()
        elif control_id == self.url_button_id:
            self.set_url()
        elif control_id == self.path_button_id:
            self.set_path()

    def onAction(self, action):
        if action.getId() in [ACTION_PARENT_DIR, KEY_NAV_BACK, ACTION_PREVIOUS_MENU]:
            self.cancelled()

    def set_option_1(self):
        self.getControl(self.url_button_id).setLabel("\r")
        self.getControl(self.radio_button_1_id).setSelected(True)
        self.getControl(self.radio_button_2_id).setSelected(False)
        self.type = 1

    def get_url(self):
        url = self.getControl(self.url_button_id).getLabel()
        if url.startswith("\r"):
            url = url[1:]
        return url

    def set_option_2(self):
        self.getControl(self.radio_button_1_id).setSelected(False)
        self.getControl(self.radio_button_2_id).setSelected(True)
        self.type = 2

    def set_url(self):
        default = self.getControl(self.url_button_id).getLabel()
        url = xbmcgui.Dialog().input(utils.ADDON_NAME, default)
        if url != "":
            self.getControl(self.url_button_id).setLabel(url)

    def set_path(self):
        fn = xbmcgui.Dialog().browse(1, utils.translate(30000), "files", ".pdf", False, False,
                                     os.path.expanduser("~")).decode('utf-8')
        if fn != "":
            self.getControl(self.path_button_id).setLabel(fn)

    def get_path(self):
        return self.getControl(self.path_button_id).getLabel()

    def cancelled(self):
        self.type = 0
        self.close()

    def ok(self):
        if self.type == 1:
            self.ret_val = self.get_url()
        elif self.type == 2:
            self.ret_val = self.get_path()
        self.close()
