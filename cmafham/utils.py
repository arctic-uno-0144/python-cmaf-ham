"""
CmafHam helper functions.

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
"""

import os
import json
import re
import io
from uuid import uuid4
from typing import Union, List
import requests


def gen_uuid() -> str:
    """ Generate a random uuid string.
    :returns: version 4(random) uuid string.
    :rtype: str
    """
    return str(uuid4())


def get_manifest_string(manifest_uri: str) -> str:
    """ Load a manifest as a string from a file or url.

    :param str manifest_uri: web url or uri path of manifest.
    :returns: string of the manifest or an empty string.
    :rtype: str
    """
    if "http" in manifest_uri:
        res = requests.get(manifest_uri, timeout=10)
        if res and res.text:
            return res.text
    if os.path.exists(manifest_uri):
        with open(manifest_uri, "r") as file:
            return file.read()
    return ""


def load_file(file_uri: str) -> Union[io.BufferedReader, io.BytesIO, None]:
    """ Download or open a file-like object.

    :param str file_uri : str - url or path to file.
    :returns: file like object or nothing if unsucessful.
    :rtype: io.BufferedReader or io.BytesIO or None
    """
    if "http" in file_uri:
        head = requests.head(file_uri, timeout=20)
        if head and hasattr(head, "headers"):
            size = head.headers.get("Content-Length")
            if size and int(size) < 536870912:
                # limit to < 500 MB for now..
                res = requests.get(file_uri, timeout=20)
                if res and res.content:
                    return io.BytesIO(res.content)
    if os.path.exists(file_uri):
        return open(file_uri, "rb")
    return None


def float_fr(framerate: Union[float, int, str]) -> float:
    """ Parse various frame rate representations and return as float value.

    :param framerate:  video frame rate.
    :type framerate: float or int or str
    :returns: float value of framerate if parsed, else 0.0.
    :rtype: float
    """
    if isinstance(framerate, float):
        # ex. 30.0, 29.97
        return framerate
    if isinstance(framerate, int):
        # ex. 25, 30
        return float(framerate)
    if isinstance(framerate, str):
        if "/" in framerate:
            # ex. "30000/1001"
            res = re.search(r'([0-9]+)/([0-9]+)', framerate)
            if res and hasattr(res, "group"):
                val = int(res.group(1)) / int(res.group(2))
                return float(val)
        else:
            # ex. "25", "59.94"
            res = re.search(r'[0-9]+', framerate)
            if res and hasattr(res, "group"):
                return float(res.group(0))
    return 0.0


def parse_codec(codec_string: str) -> List[tuple]:
    """ Return the codec(s) and their type from a string.

    :param str codec_string: mime type codec string.
    :returns: list of present codecs and their type.
    :rtype: list[tuple]
    """
    parsed: list = []
    if isinstance(codec_string, str):
        video_codecs = ("avc", "hvc", "hevc", "AVC", "HVC", "HEVC")
        audio_codecs = ("mp4a", "MP4A", "m4a", "M4A")
        text_codecs = ("wvtt", "vtt", "WEBVTT", "WVTT", "VTT", "WebVTT)
        for codec in codec_string.split(","):
            if any(v in codec for v in video_codecs):
                parsed.append(("video", codec))
            if any(a in codec for a in audio_codecs):
                parsed.append(("audio", codec))
            if any(t in codec for t in text_codecs):
                parsed.append(("text", codec))
    return parsed


def remove_ext(filename: str) -> str:
    """ Remove the extension of a filename.

    :param str filename: full uri of file.
    :returns: tail of path(filename) without extension.
    :rtype: str
    """
    res = os.path.splitext(filename)
    return res[0]


def get_path(file_path: str = "") -> str:
    """ Obtain the base path by removing the filename, otherwise, return the current dir.

    :param str file_path: uri of the file
    :returns: base path to parent file, or cwd
    :rtype: str
    """
    path = os.getcwd()
    if file_path:
        res = os.path.split(file_path)
        if res and res[0]:
            path = res[0]
    return path
    
