"""
CmafHam object models for the CMAF Presentation structure and the HLS and DASH containers.

[CMAF] ISO/IEC 23000-19:2020, Information technology — Coding of audio-visual
objects — Part 19: Common media application format (CMAF) for
segmented media.

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
"""

import os
from json import dumps as json_dumps
from typing import Union, List

from m3u8 import load, loads
from m3u8.model import M3U8, Media, Playlist
from mpegdash.parser import MPEGDASHParser
from mpegdash.nodes import MPEGDASH

from .utils import get_path


HAM_VERSION = "0.0.1"


class InputMissingError(Exception):
    """ Raised when no manifest is supplied for object creation. """
    pass


class HlsMedia:
    """ Container for a 'm3u8.model.Media' object and its corresponding 'm3u8.model.M3U8' playlist object.

    :param media: EXT-X-MEDIA object from the multivariant playlist.
    :type media: m3u8.model.Media
    :param medialist: 'M3U8' playlist for the 'Media' object content.
    :type medialist: m3u8.model.M3U8
    """
    def __init__(self, media: Media, medialist: M3U8) -> None:
        self.media = media
        self.playlist = medialist


class HlsVariant:
    """ Container for a 'm3u8.model.Playlist' object and its corresponding 'm3u8.model.M3U8' playlist object.

    :param plist: 'Playlist' object representing a variant playlist.
    :type plist: m3u8.model.Playlist
    :param playlist: 'M3U8' playlist object for the variant playlist.
    :type playlist: m3u8.model.M3U8
    """
    def __init__(self, plist: Playlist, playlist: M3U8) -> None:
        self.plist = plist
        self.variant = playlist


class HLS:
    """ Base class for containing all HLS data.

    :param str uri: uri/url of the m3u8 manifest.
    :param str string: string of the m3u8 manifest.
    :param variants: strings of the variant playlists.
    :type variants: list[str]
    :param media: strings of the media playlists.
    :type media: list[str]
    :param m3u8_obj: a m3u8.model.M3U8 object that has already been created.
    :type m3u8_obj: m3u8.model.M3U8
    :raises InputMissingError: when no input manifest or object is provided.
    """
    def __init__(
            self,
            uri: str = None,
            string: str = None,
            variants: List[str] = None,
            media: List[str] = None,
            m3u8_obj: M3U8 = None) -> None:
        if not any(x for x in (m3u8_obj, uri, string)):
            raise InputMissingError(
                "Required arguement 'uri', 'string', or 'm3u8_obj' missing!")
        if m3u8_obj:
            self.m3u8 = m3u8_obj
            self.manifest = m3u8_obj.dumps()
            # self.media = self._load_media()
            # self.variants = self._load_playlists()
        elif uri:
            if not os.path.exists(uri):
                raise InputMissingError(f"File not found at '{uri}', check path.")
            self.m3u8 = load(uri)
            self.manifest = self.m3u8.dumps()
            # self.media = self._load_media()
            # self.variants = self._load_playlists()
        elif string:
            # self.manifest = string
            # self.m3u8 = loads(string)
            # self.media = self._loads_media(media)
            # self.variants = self._loads_playlists(variants)
            raise NotImplementedError("Parsing from strings is not implemented yet!")

    def _load_media(self) -> List[HlsMedia]:
        """ Load any EXT-X-MEDIA media playlists.

        :returns: List of 'HlsMedia' objects for the HLS presentation.
        :rtype: list[cmafham.models.HlsMedia]
        """
        hls_media: list[HlsMedia] = []
        if self.m3u8.media:
            for media in self.m3u8.media:
                medialist = None
                base_uri = get_path()
                if media.base_uri:
                    base_uri = media.base_uri
                if media.uri:
                    medialist = load(base_uri+media.uri)
                media_obj = HlsMedia(media, medialist)
                if media_obj:
                    hls_media.append(media_obj)
        return hls_media

    def _loads_media(self, media_playlists) -> List[HlsMedia]:
        """ Load any EXT-X-MEDIA media playlists from strings.

        :returns: List of 'HlsMedia' objects for the HLS presentation.
        :rtype: list[cmafham.models.HlsMedia] or None
        """
        hls_media: list[HlsMedia] = []
        # if media_playlists and self.m3u8.media:
        #     # media is the m3u8.model.Media object from the multivariant
        #     for media in self.m3u8.media:
        #         # playlist is the media playlist string
        #         for playlist in media_playlists:
        #             medialist = loads(playlist, uri=base_uri)
        #             media_obj = HlsMedia(media, medialist)
        #             if media_obj:
        #                 hls_media.append(media_obj)
        return hls_media

    def _load_playlists(self) -> List[HlsVariant]:
        """ Load any EXT-X-MEDIA playlists.

        :returns: List of 'HlsVariant' objects for the HLS presentation.
        :rtype: list[cmafham.models.HlsVariant] or None
        """
        hls_variants: list[HlsVariant] = []
        return hls_variants

    def _loads_playlists(self) -> List[HlsVariant]:
        """ Load any EXT-X-MEDIA playlists from strings.

        :returns: List of 'HlsVariant' objects for the HLS presentation.
        :rtype: list[cmafham.models.HlsVariant] or None
        """
        hls_variants: list[HlsVariant] = []
        return hls_variants


class DASH:
    """ Base class to contain all DASH data.

    :param str uri: uri/url of the mpd manifest.
    :param str string: string of the mpd manifest.
    :param mpd_obj: MPEGDASH object already created from manifest.
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
    """ CMAF Segment

    (from [CMAF]) CMAF Addressable Media Object
    consisting of one or more consecutive CMAF Fragments
    from the same CMAF Track.

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

    def as_dict(self):
        """ Return as a dictionary. """
        return {
            "filename": self.filename,
            "duration": self.duration,
            "url": self.url,
            "byterange": self.byterange
        }


class AudioTrack:
    """ CMAF Audio Track

    (from [CMAF]) Sequence of CMAF Fragments that are
    consecutive in presentation time, contain one media
    stream, conform to at least one structural CMAF brand,
    including an associated CMAF Header that can initialize
    playback.

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

    def as_dict(self):
        """ Return as a dictionary. """
        segments: list = []
        if self.segments:
            segments = [s.as_dict() for s in self.segments]
        return {
            "id": self.id,
            "codec": self.codec,
            "duration": self.duration,
            "language": self.language,
            "segments": segments,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bandwidth": self.bandwidth,
            "url_init": self.url_init,
            "filename": self.filename,
            "base_uri": self.base_uri
        }


class TextTrack:
    """ CMAF Text Track

    (from [CMAF]) Sequence of CMAF Fragments that are
    consecutive in presentation time, contain one media
    stream, conform to at least one structural CMAF brand,
    including an associated CMAF Header that can initialize
    playback.
    
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

    def as_dict(self):
        """ Return as a dictionary. """
        segments: list = []
        if self.segments:
            segments = [s.as_dict() for s in self.segments]
        return {
            "id": self.id,
            "codec": self.codec,
            "duration": self.duration,
            "language": self.language,
            "segments": segments,
            "filename": self.filename,
            "base_uri": self.base_uri
        }


class VideoTrack:
    """ CMAF Video Track

    (from [CMAF]) Sequence of CMAF Fragments that are
    consecutive in presentation time, contain one media
    stream, conform to at least one structural CMAF brand,
    including an associated CMAF Header that can initialize
    playback.

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

    def as_dict(self):
        """ Return as a dictionary. """
        segments: list = []
        if self.segments:
            segments = [s.as_dict() for s in self.segments]
        return {
            "id": self.id,
            "codec": self.codec,
            "duration": self.duration,
            "language": self.language,
            "bandwidth": self.bandwidth,
            "segments": segments,
            "width": self.width,
            "height": self.height,
            "framerate": self.framerate,
            "par": self.par,
            "sar": self.sar,
            "scan_type": self.scan_type,
            "filename": self.filename,
            "base_uri": self.base_uri 
        }


class SwitchingSet:
    """ CMAF Switching Set

    (from [CMAF]) Set of one or more CMAF Tracks, where
    each track is an alternative encoding of the same source
    content, and are constrained to enable seamless track
    switching.

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

    def as_dict(self):
        """ Return as a dictionary. """
        tracks: list = []
        if self.tracks:
            tracks = [t.as_dict() for t in self.tracks]
        return {
            "id": self.id,
            "track_type": self.track_type,
            "tracks": tracks
        }


class SelectionSet:
    """ CMAF Selection Set

    (from [CMAF]) Set of one or more CMAF Switching Sets,
    where each CMAF Switching Set encodes an alternative
    aspect of the same presentation over the same time
    period, only one of which is intended to be played at a
    time, e.g. an alternative language or codec.

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

    def as_dict(self):
        """ Return as dictionary. """
        switching_sets: list[SwitchingSet] = []
        if self.switching_sets:
            switching_sets = [
                sw.as_dict() for sw in self.switching_sets
            ]
        return {
            "id": self.id,
            "switching_sets": switching_sets
        }


class Presentation:
    """ CMAF Presentation

    (from [CMAF]) Set of one or more CMAF Selection Sets
    that can be simultaneously decoded to produce a
    multimedia user experience, potentially including
    synchronized audio, video, and subtitles.

    :param str id_: presentation id, version 4 uuid.
    :param selection_sets: 'SelectionSet'(s) for the Presentation.
    :type selection_sets: list[SelectionSet] 
    """
    def __init__(self,
                 id_: str,
                 selection_sets: list[SelectionSet]) -> None:
        self.id = id_
        self.selection_sets = selection_sets
        self.data = self.as_dict()
        self.manifest = self._manifest()
    
    def as_dict(self):
        """ Return as dictionary. """
        selection_sets: list[SelectionSet] = []
        if self.selection_sets:
            selection_sets = [
                slset.as_dict() for slset in self.selection_sets]
        return {
            "id": self.id,
            "selection_sets": selection_sets
        }

    def _manifest(self) -> str:
        """ Create the CMAF-HAM Presentation manifest. """
        return json_dumps({"ham_version": HAM_VERSION, "presentation": self.data}, default=str)
