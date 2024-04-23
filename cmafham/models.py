"""
models.py
================================================================================

CmafHam object models for the CMAF Presentation structure and the HLS and DASH containers.

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
"""

from typing import Union, List
from m3u8 import load, loads
from m3u8.model import M3U8
from mpegdash.parser import MPEGDASHParser
from mpegdash.nodes import MPEGDASH


class InputMissingError(Exception):
    """ Raised when no manifest is supplied for object creation. """
    pass


class HLS:
    """ Base class to contain all HLS data

    TODO:  how to update the object with any changes

    :param str uri: uri/url of the m3u8 manifest.
    :param str string: string of the m3u8 manifest.
    :param variants: strings of the variant playlists.
    :type variants: list[str]
    :param media: strings of the media playlists.
    :type media: list[str]
    :param m3u8_obj: a m3u8.model.M3U8 object that has already been created.
    :type m3u8_obj: m3u8.model.M3U8
    :raises NotImplementedError: when trying to load from a string.
    :raises InputMissingError: when no input manifest or object is provided
    """
    def __init__(
            self,
            uri: str = None,
            string: str = None,
            variants: List[str] = None,
            media: List[str] = None,
            m3u8_obj: M3U8 = None) -> None:
        if m3u8_obj:
            self.m3u8 = m3u8_obj
            self.manifest = m3u8_obj.dumps()
        elif uri:
            self.m3u8 = load(uri)
            self.manifest = self.m3u8.dumps()
        elif string:
            # self.manifest = string
            # self.m3u8 = loads(string)
            # TODO: parse variants and media as well..
            raise NotImplementedError("Loading from strings not implemented!")
        else:
            raise InputMissingError(
                "Required arguement 'uri', 'string', or 'm3u8_obj' missing!")


class DASH:
    """ Base class to contain all DASH data

    :param str uri: uri/url of the mpd manifest
    :param str string: string of the mpd manifest
    :param mpd_obj: MPEGDASH object already created from manifest
    :type mpd_obj: mpegdash.nodes.MPEGDASH 
    """
    def __init__(
            self,
            uri: str = None,
            string: str = None,
            mpd_obj: MPEGDASH = None) -> None:
        if mpd_obj:
            self.mpd = mpd_obj
            self.manifest = MPEGDASHParser.get_as_doc(mpd_obj).toxml()
        elif uri:
            self.mpd = MPEGDASHParser.parse(uri)
            self.manifest = MPEGDASHParser.get_as_doc(self.mpd).toxml()
        elif string:
            self.mpd = MPEGDASHParser.parse(string)
            self.manifest = string
        else:
            raise InputMissingError(
                "Required arguement 'uri' or 'string' missing!")


class Segment:
    """ CMAF SEGMENT

    :param str filename: filename of the segment
    :param duration: segment duration in seconds.
    :type duration: float or int
    :param str url: full url/uri of segment.
    :param str byterange: byterange of segment.
    :param flags: helper/optional flags for format specfic mapping.
    """
    def __init__(self,
                 filename: str = "",
                 duration: Union[float, int] = 0.0,
                 url: str = "",
                 byterange: str = None,
                 **flags
                 ) -> None:
        self.filename = filename
        self.duration = float(duration)
        self.url = url
        self.byterange = byterange
        self.flags = flags


class AudioTrack:
    """ CMAF AUDIO TRACK

    :param str id_: track id, hls=group_id.
    :param str codec: audio codec.
    :param int channels: number of audio channels.
    :param duration: track duration in seconds.
    :type duration: float or int
    :param str language: audio language.
    :param segments: CMAF Segment objects for the track.
    :type segments: list[cmafham.models.Segment]
    :param sample_rate: audio sample rate.
    :type sample_rate: float or int
    :param int bandwidth: track bandwith.
    :param str url_init: uri/url of initilization segment.
    :param flags: helper/optional flags for format specfic mapping.
    """
    def __init__(self,
                 id_: str = "",
                 codec: str = "",
                 channels: int = 0,
                 duration: Union[float, int] = 0.0,
                 language: str = "",
                 segments: List[Segment] = None,
                 sample_rate: Union[float, int] = 0.0,
                 bandwidth: int = 0,
                 url_init: str = "",
                 filename: str = "",
                 base_uri: str = "",
                 **flags
                 ) -> None:
        self.id = id_
        self.codec = codec
        self.duration = float(duration)
        self.language = language
        self.segments = segments
        self.sample_rate = sample_rate
        self.channels = channels
        self.bandwidth = bandwidth
        self.url_init = url_init
        self.filename = filename
        self.base_uri = base_uri
        self.flags = flags


class TextTrack:
    """ CMAF TEXT TRACK
    
    :param str id_: track id, hls=group_id.
    :param str codec: subtitle codec or embedded captions.
    :param duration: track duration.
    :type duration: float or int
    :param str language: subtitle language.
    :param segments: CMAF Segment objects for the track.
    :type segments: cmafham.models.Segment
    :param flags: helper/optional flags for format specfic mapping.
    """
    def __init__(self,
                 id_: str = "",
                 codec: str = "",
                 duration: Union[float, int] = 0.0,
                 language: str = "",
                 segments: List[Segment] = None,
                 filename: str = "",
                 base_uri: str = "",
                 **flags
                 ) -> None:
        self.id = id_
        self.codec = codec
        self.duration = float(duration)
        self.language = language
        self.segments = segments
        self.filename = filename
        self.base_uri = base_uri
        self.flags = flags


class VideoTrack:
    """ CMAF VIDEO TRACK

    :param str id_: video track id, hls=version 4 uuid.
    :param str codec: video codec.
    :param duration: track duration.
    :type duration: float or int
    :param str language: video language.
    :param int bandwidth: track bandwidth.
    :param segments: CMAF Segment objects for the track.
    :type segments: cmafham.models.Segment
    :param int width: video width.
    :param int height: video height.
    :param framerate: video frame rate.
    :type framerate: float or int.
    :param str par: video par.
    :param str sar: video sar.
    :param str scan_type: video scan type ("interlaced" | "progressive").
    :param flags: helper/optional flags for format specfic mapping.
    """
    def __init__(self,
                 id_: str = "",
                 codec: str = "",
                 duration: Union[float, int] = 0.0,
                 language: str = "",
                 bandwidth: int = 0,
                 segments: list[Segment] = None,
                 width: int = 0,
                 height: int = 0,
                 framerate: Union[float, int] = 0.0,
                 par: str = "",
                 sar: str = "",
                 scan_type: str = "",
                 filename: str = "",
                 base_uri: str = "",
                 **flags
                 ) -> None:
        self.id = id_
        self.codec = codec
        self.duration = float(duration)
        self.language = language
        self.bandwidth = bandwidth
        self.segments = segments
        self.width = width
        self.height = height
        self.framerate = float(framerate)
        self.par = par
        self.sar = sar
        self.scan_type = scan_type
        self.filename = filename
        self.base_uri = base_uri
        self.flags = flags


class SwitchingSet:
    """ CMAF SWITCHING SET

    :param str id_: switching set id, version 4 uuid.
    :param str track_type: type of the tracks ("audio" | "text" | "video")
    :param tracks: tracks for the 'SwitchingSet'.
    :type tracks: list[cmafham.models.AudioTrack] or list[cmafham.models.TextTrack] or list[cmafham.models.TextTrack]
    """
    def __init__(self,
                 id_: str,
                 track_type: str,
                 tracks: Union[List[AudioTrack], List[TextTrack], List[VideoTrack]]
                 ) -> None:
        self.id = id_
        self.tracks = tracks
        self.track_type = track_type


class SelectionSet:
    """ CMAF SELECTION SET

    :param str id_: switching set id, version 4 uuid.
    :param switching_sets: 'SwitchingSet'(s) for the 'SelectionSet'.
    :type switching_sets: list[cmafham.models.SwitchingSet]
    """
    def __init__(self,
                 id_: str,
                 switching_sets: list[SwitchingSet]
                 ) -> None:
        self.id = id_
        self.switching_sets = switching_sets


class Presentation:
    """ CMAF PRESENTATION

    :param str id_: presentation id, version 4 uuid.
    :param selection_sets: 'SelectionSet'(s) for the Presentation.
    :type selection_sets: list[SelectionSet] 
    """
    def __init__(self,
                 id_: str,
                 selection_sets: list[SelectionSet]
                 ) -> None:
        self.id = id_
        self.selection_sets = selection_sets
