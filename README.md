# PDF Reader

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ed2697c44e8745d88e19d8f076116171)](https://www.codacy.com/app/i96751414/plugin.image.pdfreader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=i96751414/plugin.image.pdfreader&amp;utm_campaign=Badge_Grade)
[![Build Status](https://github.com/i96751414/plugin.image.pdfreader/workflows/build/badge.svg)](https://github.com/i96751414/plugin.image.pdfreader/actions?query=workflow%3Abuild)

Read your pdf's (ebooks) through Kodi

![logo](https://github.com/i96751414/plugin.image.pdfreader/raw/master/icon.png)

PDF Reader is an add-on (image plugin) for Kodi capable of reading PDFs composed of images (e.g. scans, comics). It also serves as a module, so it can be called from other add-ons (see [API](#api) section).

More info can be found in Kodi's [forum](https://forum.kodi.tv/showthread.php?tid=187421).

Limitations
-----------
- Currently PDF Reader can only read pdf files made of pictures, since its operation method's consists of extracting pictures from PDF files.
- Only JPG and PNG types are supported at the moment. If you want to add a new image type, just say.

Download
--------
See the [Releases](https://github.com/i96751414/plugin.image.pdfreader/releases) page.

<a name="api"></a> API
----------------------
PDF reader can be called from other add-ons regardless their type. To do so, the `addon.xml` must contain the following line:
```xml
<requires>
    ...
    <import addon="plugin.image.pdfreader"/>
</requires>
```
Then, just `import pdf` and use the available methods:
```python
# PDF Reader class
PDFReader()
  read(path)
  info()
  name()
  convert_to_images(save_path=None)
  clean_temp()

# CBR/CBZ Reader class
CBXReader()
  read(path)
  info()
  name()
  convert_to_images(save_path=None)
  clean_temp()

# Play PDF function - can be called regardless the add-on type
# path: PDF url or file path
# compress: Compress data paths when sending request
# is_image_plugin: Set to true if the caller plugin is an image plugin
# return: bool - success
play_pdf(path, compress=True, is_image_plugin=False)
```

Screenshots
-----------

![screen1](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-1.png)

![screen2](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-2.png)

![screen3](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-3.png)

![screen4](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-4.png)