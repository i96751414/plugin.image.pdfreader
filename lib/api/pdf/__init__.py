import base64
import json
import os
import re
import shutil
import sys
import time
import zlib

try:
    from urllib import quote_plus, urlretrieve
except ImportError:
    from urllib.parse import quote_plus
    from urllib.request import urlretrieve

import xbmc
import xbmcaddon
import xbmcgui

from . import utils

# File signatures
FILE_SIGNATURES = [
    {"type": "jpg", "start_mark": b"\xff\xd8", "end_mark": b"\xff\xd9", "end_fix": 2},
    {"type": "png", "start_mark": b"\x89\x50\x4E\x47", "end_mark": b"\xAE\x42\x60\x82", "end_fix": 4},
]


class StopDownloadError(Exception):
    pass


class DownloadProgress(object):
    def __init__(self, dialog_progress, rate_window=2):
        self._dialog = dialog_progress
        self._rate_window = rate_window
        self._last_time = time.time()
        self._last_block = 0
        self._percent = 0
        self._percent_last_time = self._last_time

    def _update_percent(self, increment=10, update_rate=0.5, current_time=None):
        if current_time is None:
            current_time = time.time()
        if current_time - self._percent_last_time >= update_rate:
            self._percent_last_time = current_time
            self._percent += increment
            if self._percent > 100:
                self._percent = 0

    def __call__(self, block_num, block_size, file_size):
        current_time = time.time()
        time_passed = current_time - self._last_time
        if time_passed == 0:
            return

        total_downloaded = block_num * block_size
        total_downloaded_mb = total_downloaded / (1024.0 * 1024.0)
        bps = (block_num - self._last_block) * block_size / time_passed

        if time_passed >= self._rate_window:
            self._last_block = block_num
            self._last_time = current_time

        if file_size <= 0:
            percent = self._percent
            self._update_percent(current_time=current_time)
            status = "%.02f MB downloaded (%.0f kB/s)\n%s: --:--\n\n" % (
                total_downloaded_mb, (bps / 1024.0), utils.translate(30020))
        else:
            percent = min(total_downloaded * 100 // file_size, 100)
            remaining_size = file_size - total_downloaded
            eta = remaining_size / bps if bps > 0 and remaining_size > 0 else 0
            minutes, seconds = divmod(eta, 60)
            status = "%.02f MB %s %.02f MB (%.0f kB/s)\n%s: %02d:%02d\n\n" % (
                total_downloaded_mb, utils.translate(30021), file_size / (1024.0 * 1024.0), (bps / 1024.0),
                utils.translate(30020), minutes, seconds)

        if self._dialog.iscanceled():
            raise StopDownloadError("Stopped Downloading")
        self._dialog.update(percent, status)


class PDFReader(object):
    min_size = 10000

    def __init__(self):
        # Path of local pdf
        self._file_path = ""
        # Temp path
        self._temp_path = os.path.join(utils.DATA_PATH, "temp")
        self._temp_images_path = os.path.join(self._temp_path, "images")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_temp()

    def info(self):
        pdf_content = self.read_contents()

        for t in FILE_SIGNATURES:
            if t["start_mark"] in pdf_content and t["end_mark"] in pdf_content:
                return t

        return None

    def name(self):
        if not self._file_path:
            return ""

        return os.path.splitext(os.path.basename(self._file_path))[0]

    def read_contents(self):
        if not self._file_path or not os.path.isfile(self._file_path):
            return ""

        with open(self._file_path, "rb") as fh:
            return fh.read()

    def temp(self):
        if not os.path.exists(self._temp_path):
            os.makedirs(self._temp_path)
        return self._temp_path

    def temp_images(self):
        if not os.path.exists(self._temp_images_path):
            os.makedirs(self._temp_images_path)
        return self._temp_images_path

    def clean_temp(self):
        if os.path.exists(self._temp_path):
            shutil.rmtree(self._temp_path, True)

    def read(self, path):
        if os.path.isfile(path):
            self._file_path = path
        elif path.startswith("http"):
            self._file_path = self.download(path)
        else:
            self._file_path = ""

        return bool(self._file_path)

    def convert_to_images(self, save_path=None):
        if save_path is None:
            save_path = self.temp_images()

        pdf_info = self.info()
        if pdf_info is None:
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
            i_stream = pdf.find(b"stream", i)
            if i_stream < 0:
                break
            i_start = pdf.find(start_mark, i_stream, i_stream + i_offset)
            if i_start < 0:
                i = i_stream + i_offset
                continue
            i_end_stream = pdf.find(b"endstream", i_start)
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

        return images_path

    def download(self, url, name="", ext=".pdf"):
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        url_quoted = quote_plus(url)

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

        dialog = xbmcgui.DialogProgress()
        dialog.create("Download")
        dialog.update(0)

        try:
            urlretrieve(url, path, DownloadProgress(dialog))
        except StopDownloadError:
            if os.path.exists(path):
                os.remove(path)
            return False
        finally:
            dialog.close()

        return True


class CBXReader(PDFReader):
    def __init__(self):
        super(CBXReader, self).__init__()

    def read(self, path):
        if path.lower().endswith(".cbr"):
            ext = ".cbr"
        elif path.lower().endswith(".cbz"):
            ext = ".cbz"
        else:
            return False

        if os.path.isfile(path) and path.endswith(ext):
            self._file_path = path
        elif path.startswith("http"):
            self._file_path = self.download(path, ext=ext)
        else:
            self._file_path = ""

        if self._file_path:
            xbmc.executebuiltin("Extract(%s, %s)" % (self._file_path, self.temp_images()))
            return True
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

    data = json.dumps({"images": images, "id": xbmcaddon.Addon().getAddonInfo("id")})

    if compress:
        compressed_data = utils.bytes_to_str(base64.b64encode(zlib.compress(utils.str_to_bytes(data), 9)))
        uri = "plugin://%s/play_images_z/%s" % (utils.ADDON_ID, quote_plus(compressed_data, ""))
    else:
        uri = "plugin://%s/play_images/%s" % (utils.ADDON_ID, quote_plus(data, ""))

    if is_image_plugin:
        xbmc.executebuiltin("Container.Update(%s)" % uri)
    else:
        xbmc.executebuiltin("ActivateWindow(Pictures, %s)" % uri)

    return True
