"""
CmafHam
================================================================================

A Python library for the parsing, manipulation and creation of
HLS and DASH manifests using the CMAF 'Hypothetical Application Model' as defined in ISO/IEC 23000-19.

Inspired by the Common Media Library CMAF-HAM project:
    * https://github.com/qualabs/common-media-library/tree/feature/cmaf-ham

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
:version: 0.0.1
"""
import os

from .ham import HAM, HamMapper
from .models import HLS, DASH


class InputManifestError(Exception):
    """ Exception to be raised when input is missing or for invalid manifest formats. """
    pass


class MissingSegmentError(Exception):
    """ Exception to be raised when segment files cannot be found or loaded properly. """
    pass


def load(manifest_uri: str) -> HAM:
    """ Create a 'HAM' object from a uri/url.

    :param str manifest_uri: file path or url of the manifest to use.
    :returns: 'HAM' of the source presentation containing the 'Presentation', 'HLS', and 'DASH' objects.
    :rtype: cmafham.ham.HAM
    :raises InputManifestError: When an invalid file extension is given.
    """
    if ".m3u8" in manifest_uri:
        return HamMapper.hls_to_ham(HLS(uri=manifest_uri))
    if ".mpd" in manifest_uri:
        # return HamMapper.dash_to_ham(DASH(uri=manifest_uri))
        raise NotImplementedError("Parsing from DASH is not implemented yet!")
    if ".json" in manifest_uri:
        return HamMapper.ham_manifest(uri=manifest_uri)
    raise InputManifestError(
        "Input manifest must be of type 'm3u8' or 'mpd'!")


def loads(
        manifest_string: str,
        hls_renditions: list[str] = None,
        hls_media: list[str] = None,
        file_uri: str = None) -> HAM:
    """ Create a 'HAM' object from string(s).

    :param str manifest_string: string representation of manifest.
    :param hls_renditions: strings of the HLS variant playlists, optional.
    :type hls_renditions: list[str]
    :param hls_media: strings of HLS media playlists, optional.
    :type hls_media: list[str]
    :param str file_uri: path to the media files.
    :returns: Object model of the source presentation containing the CMAF 'Presentation', 'HLS', and 'DASH' objects.
    :rtype: cmafham.ham.HAM
    :raises InputManifestError: When the manifest type can't be parsed or is invalid.
    """
    if "#EXTM3U" in manifest_string:
        raise NotImplementedError(
            "Parsing from HLS strings is not implemented yet!")
        # hls_obj = HLS(
        #     string=manifest_string,
        #     variants=hls_renditions,
        #     media=hls_media)
        # return HamMapper.hls_to_ham(hls_obj)
    if "?xml version" in manifest_string:
        raise NotImplementedError(
            "Parsing from DASH strings is not implemented yet!")
        # return HamMapper.dash_to_ham(string=manifest_string)
    if "ham_version" in manifest_string:
        return HamMapper.ham_manifest(string=manifest_string)
    raise InputManifestError(
        "Input manifest type must be one of: (m3u8, mpd, json)")


def from_segments(base_uri: str = None, segments: list[str] = None) -> HAM:
    """ NOT IMPLEMENTED!
    Create a 'HAM' object based on the segment files.

    :param str base_uri: base path location for segments.
    :param segments: list of segment filenames.
    :returns: A 'HAM' object representing the media presentation.
    :rtype: cmafham.ham.HAM
    :raises MissingSegmentError: when segment files are missing or loading fails.
    """
    # if not any((base_uri, segments)):
    #     # no path or segment names, can't continue
    #     raise MissingSegmentError(
    #         "Missing required arguement(s) 'base_uri' or 'segments'.")
    # elif base_uri and not segments:
    #     # path is given, but no filenames
    #     segments = [f for f in os.listdir(base_uri) if os.path.isfile(f)]
    # elif segments and not base_uri:
    #     # filenames are provided with no location
    #     base_uri = os.getcwd()
    # # only relevant file types
    # extensions = ("mp4", "fmp4", "cmfa", "cmfv", "vtt")
    # segments = [s for s in segments if any(ex in s for ex in extensions)]
    # return HamMapper.segments_to_ham(base_uri=base_uri, segments=segments)
    raise NotImplementedError("Parsing from segments not implemented yet!")
