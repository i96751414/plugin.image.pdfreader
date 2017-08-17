# -*- coding: UTF-8 -*-

import os
import re
import sys
import json
import time
import xbmc
import zlib
import base64
import shutil
import urllib
import xbmcgui
import xbmcaddon

try:
    from lib import utils
except ImportError:
    parent_dir = os.path.abspath(os.path.join(__file__, "../../../"))
    sys.path.insert(0, parent_dir)
    from lib import utils

# File signatures
FILE_SIGNATURES = [
    {"type": "jpg", "start_mark": "\xff\xd8", "end_mark": "\xff\xd9", "end_fix": 2},
    {"type": "png", "start_mark": "\x89\x50\x4E\x47", "end_mark": "\xAE\x42\x60\x82", "end_fix": 4},
]


class PDFReader:
    def __init__(self):
        # Path of local pdf
        self.file_path = ""

        # Temp path
        self.temp_path = os.path.join(utils.DATA_PATH, "temp")
        self.temp_images_path = os.path.join(self.temp_path, "images")

        # Minimum size for each picture
        self.min_size = 10000

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_temp()

    def info(self):
        pdf_content = self.read_contents()

        for t in FILE_SIGNATURES:
            if re.search(t["start_mark"], pdf_content) and re.search(t["end_mark"], pdf_content):
                return t

        return {}

    def name(self):
        if self.file_path == "":
            return ""

        return os.path.splitext(self.file_path)[0].replace("\\", "/").split("/")[-1]

    def read_contents(self):
        if self.file_path == "" or not os.path.isfile(self.file_path):
            return ""

        with open(self.file_path, "rb") as fh:
            return fh.read()

    def temp(self):
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
        return self.temp_path

    def temp_images(self):
        if not os.path.exists(self.temp_images_path):
            os.makedirs(self.temp_images_path)
        return self.temp_images_path

    def clean_temp(self):
        if os.path.exists(self.temp_path):
            shutil.rmtree(self.temp_path, True)

    def read(self, path):
        if os.path.isfile(path):
            self.file_path = path
        elif path.startswith("http"):
            self.file_path = self.download(path)
        else:
            self.file_path = ""

        return self.file_path != ""

    def convert_to_images(self, save_path=None):
        if save_path is None:
            save_path = self.temp_images()

        pdf_info = self.info()
        if pdf_info == {}:
            return []

        pdf_type = pdf_info["type"]
        start_mark = pdf_info["start_mark"]
        end_mark = pdf_info["end_mark"]
        end_fix = pdf_info["end_fix"]

        name = self.name()
        if not name:
            return []

        pdf = self.read_contents()
        if not pdf:
            return []

        start_fix = 0
        i = 0
        dim = 0
        i_offset = 20
        images_path = []
        while True:
            i_stream = pdf.find("stream", i)
            if i_stream < 0:
                break
            i_start = pdf.find(start_mark, i_stream, i_stream + i_offset)
            if i_start < 0:
                i = i_stream + i_offset
                continue
            i_end_stream = pdf.find("endstream", i_start)
            if i_end_stream < 0:
                raise Exception("Unable to find end of stream")
            i_end = pdf.find(end_mark, i_end_stream - i_offset)
            if i_end < 0:
                raise Exception("Unable to find end of picture")

            i_start += start_fix
            i_end += end_fix

            image = pdf[i_start:i_end]

            if utils.show_real_thumbnails() and (utils.always_refresh_thumbnails() or name == "temp"):
                # Force thumbnails to refresh by generating different names
                img_name = "%s_%d_%d.%s" % (name, dim, int(time.time()), pdf_type)
            else:
                # Using numbered thumbnails - name does not matter
                img_name = "%s_%d.%s" % (name, dim, pdf_type)

            if sys.getsizeof(image) > self.min_size or not utils.check_picture_size():
                image_path = os.path.join(save_path, img_name)
                with open(image_path, "wb") as fh:
                    fh.write(image)
                images_path.append(image_path)
                dim += 1
            i = i_end

        with open(os.path.join(self.temp(), "names.txt"), "w") as fh:
            for image_path in images_path:
                fh.write("%s\n" % image_path)

        return images_path

    def download(self, url, name="", ext=".pdf"):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        url_quoted = urllib.quote_plus(url)

        if utils.save_pdf():
            local_folder = utils.get_local_folder()
            if local_folder == "":
                xbmcgui.Dialog().ok(utils.translate(30015), utils.translate(30018))
                utils.open_settings()
                return ""

            db = os.path.join(local_folder, "pdfreader_db.txt")
            if os.path.isfile(db):
                with open(db, "r+") as fh:
                    db_content = fh.read()
                    # Check if the file was already downloaded
                    match = re.compile('<path="(.+?)" url="%s"/>' % url_quoted).findall(db_content)
                    if len(match) > 0:
                        stored_path = match[0]
                        if os.path.isfile(os.path.join(local_folder, stored_path)):
                            return stored_path
                        else:
                            # If the file does not exists, delete the entry from db
                            fh.seek(0)
                            fh.write(db_content.replace('<path="%s" url="%s"/>' % (stored_path, url_quoted), ""))
                            fh.truncate()

            name += "%s%d%s" % ("_" if name else "", int(time.time()), ext)
            path = os.path.join(local_folder, name)
            if self._download(url, path):
                # Update db if download succeeded
                with open(db, "a") as fh:
                    fh.write('<path="%s" url="%s"/>' % (name, url_quoted))
                return path
        else:
            if not name:
                name = "temp"
            path = os.path.join(self.temp(), name + ext)

            if self._download(url, path):
                return path

        return ""

    def _download(self, url, path):
        if os.path.isfile(path):
            if path.startswith(self.temp()):
                os.remove(path)
            else:
                xbmcgui.Dialog().ok(utils.translate(30015), utils.translate(30019))
                return False

        dp = xbmcgui.DialogProgress()
        dp.create("Download")
        dp.update(0)

        try:
            st = time.time()
            urllib.urlretrieve(url, path, lambda nb, bs, fs: self._dialog_download(nb, bs, fs, dp, st))
        except self.StopDownloading:
            if os.path.exists(path):
                os.remove(path)
            dp.close()
            return False

        dp.close()
        return True

    def _dialog_download(self, num_blocks, block_size, file_size, dialog_progress, start_time):
        percent = min(num_blocks * block_size * 100 / file_size, 100)
        currently_downloaded = float(num_blocks) * block_size / (1024 * 1024)
        kbps_speed = num_blocks * block_size / (time.time() - start_time)
        if file_size < 0:
            mbs = "%.02f MB downloaded (%.0f kB/s)" % (currently_downloaded, (kbps_speed / 1024))
            time_left = "%s: --:--" % (utils.translate(30020))
        else:
            if kbps_speed > 0:
                eta = (file_size - num_blocks * block_size) / kbps_speed
            else:
                eta = 0
            total = float(file_size) / (1024 * 1024)

            mbs = "%.02f MB %s %.02f MB (%.0f kB/s)" % (
                currently_downloaded, utils.translate(30021), total, (kbps_speed / 1024))

            minutes, seconds = divmod(eta, 60)
            time_left = "%s: %02d:%02d" % (utils.translate(30020), minutes, seconds)

        dialog_progress.update(percent, mbs, time_left)

        if dialog_progress.iscanceled():
            dialog_progress.close()
            raise self.StopDownloading("Stopped Downloading")

    class StopDownloading(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)


class CBXReader(PDFReader):
    def __init__(self):
        PDFReader.__init__(self)

    def read(self, path, ext=".cbr"):
        if os.path.isfile(path) and path.endswith(ext):
            self.file_path = path
        elif path.startswith("http"):
            self.file_path = self.download(path, ext=ext)
        else:
            self.file_path = ""

        if self.file_path:
            xbmc.executebuiltin("Extract(%s, %s)" % (self.file_path, self.temp_images()))
            return True
        else:
            return False

    def convert_to_images(self, save_path=None):
        images_path = []

        if save_path is not None and not os.path.isdir(save_path):
            save_path = None

        for f in os.listdir(self.temp_images()):
            file_path = os.path.join(self.temp_images(), f)

            if os.path.getsize(file_path) > self.min_size or not utils.check_picture_size():
                if save_path is not None:
                    shutil.copyfile(file_path, os.path.join(save_path, f))
                images_path.append(file_path)
        return images_path

    def info(self):
        return {"type": "cbx"}


def error_message():
    dialog = xbmcgui.Dialog()
    dialog.ok(utils.translate(30002), utils.translate(30038))


def play_pdf(path, compress=True, is_image_plugin=False):
    reader = PDFReader()
    reader.clean_temp()
    if not reader.read(path):
        error_message()
        return False

    images = reader.convert_to_images()
    if not images:
        error_message()
        return False

    data = json.dumps({
        "images": images,
        "id": xbmcaddon.Addon().getAddonInfo("id"),
    })

    if compress:
        compressed_data = base64.b64encode(zlib.compress(data, 9))
        uri = "plugin://%s/play_images_z/%s" % (utils.ADDON_ID, urllib.quote_plus(compressed_data, ""))
    else:
        uri = "plugin://%s/play_images/%s" % (utils.ADDON_ID, urllib.quote_plus(data, ""))

    if is_image_plugin:
        xbmc.executebuiltin("Container.Update(%s)" % uri)
    else:
        xbmc.executebuiltin("ActivateWindow(Pictures, %s, return)" % uri)

    return True
