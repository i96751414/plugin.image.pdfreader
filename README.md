# PDF Reader

[![Build Status](https://github.com/i96751414/plugin.image.pdfreader/workflows/build/badge.svg)](https://github.com/i96751414/plugin.image.pdfreader/actions?query=workflow%3Abuild)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d5b5db57e38e495aade6c3747422047c)](https://www.codacy.com/gh/i96751414/plugin.image.pdfreader/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=i96751414/plugin.image.pdfreader&amp;utm_campaign=Badge_Grade)

Read your pdf's (ebooks) through Kodi

![logo](https://github.com/i96751414/plugin.image.pdfreader/raw/master/icon.png)

PDF Reader is an add-on (image plugin) for Kodi capable of reading PDFs composed of images (e.g. scans, comics). It also serves as a module, so it can be called from other add-ons (see [API](#api) section).

More info can be found in Kodi's [forum](https://forum.kodi.tv/showthread.php?tid=187421).

## Limitations

-   Currently PDF Reader can only read pdf files made of pictures, since its operation method's consists of extracting pictures from PDF files.
-   Only JPG and PNG types are supported at the moment. If you want to add a new image type, just say.

## Installation

The recommended way of installing this addon is through
its [repository](https://github.com/i96751414/repository.github#installation). This way, any updates will be
automatically installed.

Although **not recommended**, one can install the addon without installing its repository. To do so, get
the [latest release](https://github.com/i96751414/plugin.image.pdfreader/releases/latest) from github. Please note
that, if there are any additional dependencies, they won't be resolved unless the repository is installed.

## <a name="api"></a> API

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

## Screenshots

![screen1](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-1.png)

![screen2](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-2.png)

![screen3](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-3.png)

![screen4](https://github.com/i96751414/plugin.image.pdfreader/raw/master/resources/img/screenshot-4.png)
