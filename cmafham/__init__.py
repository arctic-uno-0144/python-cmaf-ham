"""
CmafHam
================================================================================

A Python library for the parsing, manipulation and creation of
HLS and DASH manifests using the CMAF Hypothetical Application Model(ISO/IEC 23000-19).

Inspired by the Common Media Library CMAF-HAM project:
    - https://github.com/qualabs/common-media-library/tree/feature/cmaf-ham

Credit to the 'm3u8' and 'mpegdash' libraries for parsing and rendering:
    - https://github.com/globocom/m3u8
    - https://github.com/sangwonl/python-mpegdash/tree/master

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
:version: 0.0.1
"""
from .ham import HAM, HamMapper
from .models import HLS, DASH


class InputManifestError(Exception):
    """ Exception for invalid manifest formats. """
    pass


def load(manifest_uri: str) -> HAM:
    """ Create a HAM object from a uri/url.

    :param str manifest_uri: file path or url of the manifest to load
    :returns: 'HAM' of the source presentation containing the cmafham.models.Presentation, cmafham.models.HLS, and cmafham.models.DASH objects
    :rtype: cmafham.ham.HAM
    :raises InputManifestError: When an invalid file extension is given
    """
    if ".m3u8" in manifest_uri:
        return HamMapper.hls_to_ham(HLS(uri=manifest_uri))
    if ".mpd" in manifest_uri:
        # return HamMapper.dash_to_ham(DASH(uri=manifest_uri))
        raise NotImplementedError("Parsing from DASH is not implemented yet!")
    raise InputManifestError(
        "Input manifest must be of type 'm3u8' or 'mpd'!")


def loads(
        manifest_string: str,
        hls_renditions: list[str] = None,
        hls_media: list[str] = None) -> HAM:
    """ NOT IMPLEMENTED! Create a HAM object from string(s)

    :param str manifest_string: string representation of manifest
    :param hls_renditions: strings of hls variant playlists (optional)
    :type hls_renditions: list[str]
    :param hls_media: strings of hls media playlists (optional)
    :type hls_media: list[str]
    :returns: Object model of the source presentation containing the CMAF 'Presentation', 'HLS', and 'DASH' objects
    :rtype: cmafham.ham.HAM
    :raises NotImplementedError: Parsing from manifest strings is not implemented yet.
    """
    # if "#EXTM3U" in manifest_string:
    #     hls_obj = HLS(
    #         string=manifest_string,
    #         variants=hls_renditions,
    #         media=hls_media)
    #     return HamMapper.hls_to_ham(hls_obj)
    # if "?xml version" in manifest_string:
    #     return HamMapper.dash_to_ham(string=manifest_string)
    # raise InputManifestError(
    #     "Input manifest must be of type m3u8 or mpd!")
    raise NotImplementedError(
        "Loading from string not implemented yet!")
