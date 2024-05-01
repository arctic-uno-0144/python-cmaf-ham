"""
This module contains the core objects and functions to perform the parsing and mapping to the models.

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
"""

import json
from math import ceil as math_ceil
from typing import Union, List
from re import search

from m3u8 import load
from m3u8.model import Segment as HlsSegment
from m3u8.model import (
    M3U8,
    Media,
    StreamInfo,
    Playlist,
    PlaylistList,
    MediaList,
    SegmentList,
    InitializationSection
)
from mpegdash.parser import MPEGDASHParser
from mpegdash.nodes import (
    MPEGDASH,
    Period,
    AdaptationSet,
    Representation
)

from .cmaf import parse_cmaf_file, CMAF
from .models import (
    Presentation,
    SwitchingSet,
    SelectionSet,
    AudioTrack,
    TextTrack,
    VideoTrack,
    Segment,
    HLS,
    DASH
)
from .utils import (
    gen_uuid,
    parse_codec,
    float_fr,
    remove_ext,
    get_path
)


class HAM:
    """ The 'Hypothetical Application Model' object is the container of the CMAF 'Presentation', 'HLS' and 'DASH' objects.

    :param presentation: The CMAF 'Presentation' object representation of the media presentation.
    :type presentation: cmafham.models.Presentation
    :param hls_obj: the 'HLS' wrapper object that contains the HLS presentation data.
    :type hls_obj: cmafham.models.HLS
    :param dash_obj: the 'DASH' wrapper object that contains the DASH presentation data.
    :type dash_obj: cmafham.models.DASH
    """
    def __init__(self,
                 presentation: Presentation,
                 hls_obj: HLS = None,
                 dash_obj: DASH = None) -> None:
        self.presentation = presentation
        self.hls = hls_obj
        self.dash = dash_obj
        # self.update()

    def update(self) -> None:
        """ Create the missing object(s) from the CMAF 'Presentation'. """
        if not self.hls:
            self.hls = HamMapper.ham_to_hls(self.presentation)
        if not self.dash:
            self.dash = HamMapper.ham_to_dash(self.presentation)

    def render_hls(self, save_to: str = None, filename: str = None) -> None:
        """ Create the manifest files for the HLS presentation.

        TODO: clean up the filename, possibly use other defaults or self.presentation.id.

        :param str save_to: path to save the manifest files to, optional, defaults to cwd.
        :param str filename: filename for the manifest, optional, defaults to 'main'.
        """
        # check and set the save path
        if save_to:
            output_path = save_to
        else:
            output_path = get_path()
        if filename:
            if ".m3u8" not in filename:
                filename += ".m3u8"
            output_path += filename
        else:
            output_path += "main.m3u8"
        with open(output_path, "w") as f:
            f.write(self.hls.manifest)
        for i, media in enumerate(self.hls.m3u8.media):
            # create media playlist files...
            continue
        for i, plist in enumerate(self.hls.m3u8.playlists):
            # create playlist files...
            continue

    def render_dash(self, save_to: str = None, filename: str = None) -> None:
        """ Create a manifest file for the DASH presentation.

        TODO: clean up the filename, possibly use other defaults or self.presentation.id

        :param str save_to: location to save the manifest file, optional, defaults to cwd.
        :param str filename: filename for the manifest, optional, defaults to 'main'.
        """
        # check and set the save path
        if save_to:
            output_path = save_to
        else:
            output_path = get_path()
        # verify extension and set filename
        if filename:
            if ".mpd" not in filename:
                filename += ".mpd"
            output_path = output_path + filename
        else:
            output_path = output_path + "main.mpd"
        # write to the file
        with open(full_path, "w") as f:
            f.write(self.dash.manifest)

    def render_ham(self, save_to: str = None, filename: str = None) -> None:
        """ Create a json manifest file of the CMAF 'Presentation'. """
        # check and set the save path
        if save_to:
            output_path = save_to
        else:
            output_path = get_path()
        # verify extension and set filename
        if filename:
            if ".json" not in filename:
                filename += ".json"
            output_path += filename
        else:
            output_path += f"{self.presentation.id}.json"
        # write to the file
        with open(output_path, "w") as f:
            json.dump(self.presentation.manifest, f, indent=2)


class HamMapper:
    """
    HLS <--> Presentation <--> DASH
    """
    @staticmethod
    def hls_to_ham(hls_obj: HLS) -> HAM:
        """ Create a 'HAM' object from the 'HLS' object.

        :param hls_obj:  object representation of HLS manifest/presentation.
        :type hls_obj: cmafham.models.HLS
        :returns: HAM object containing the CMAF 'Presentation', 'HLS', and 'DASH' representations.
        :rtype: cmafham.ham.HAM
        """
        selection_sets: list[SelectionSet] = []
        audio_sets: list[SwitchingSet] = []
        text_sets: list[SwitchingSet] = []
        video_sets: list[SwitchingSet] = []
        # check for media
        if hls_obj.m3u8.media:
            for media in hls_obj.m3u8.media:
                medialist = None
                mbase_uri: str = ""
                if media.base_uri:
                    mbase_uri = media.base_uri
                    if media.uri:
                        medialist = load(media.base_uri+media.uri)
                if media.type == "AUDIO":
                    tracks = [HlsTrackMapper.audio(
                        media=media, base_uri=mbase_uri,audiolist=medialist,
                        playlists=hls_obj.m3u8.playlists)]
                    if tracks:
                        audio_sets.append(
                            SwitchingSet(
                                id_=media.group_id,
                                track_type="audio",
                                tracks=tracks)
                        )
                if media.type in ("SUBTITLES", "CLOSED-CAPTIONS", "TEXT"):
                    tracks = [HlsTrackMapper.text(
                              media=media,
                              base_uri=mbase_uri,
                              playlist=medialist)]
                    if tracks:
                        text_sets.append(
                            SwitchingSet(
                                id_=media.group_id,
                                track_type="text",
                                tracks=tracks)
                        )
        # check the variant playlists
        if hls_obj.m3u8.playlists:
            for playlist in hls_obj.m3u8.playlists:
                vbase_uri: str = ""
                if playlist.base_uri:
                    vbase_uri = playlist.base_uri
                    variant = load(playlist.base_uri+playlist.uri)
                tracks = [HlsTrackMapper.video(
                          playlist=playlist,
                          base_uri=vbase_uri,
                          variant=variant)]
                if tracks:
                    video_sets.append(
                        SwitchingSet(
                            id_=gen_uuid(),
                            track_type="video",
                            tracks=tracks
                        )
                    )
        # add any non empty sets
        for swsets in (video_sets, audio_sets, text_sets):
            if len(swsets) > 0:
                selection_sets.append(
                    SelectionSet(id_=gen_uuid(), switching_sets=swsets)
                )
        return HAM(
            presentation=Presentation(
                id_=gen_uuid(),
                selection_sets=selection_sets
            ), 
            hls_obj=hls_obj
        )

    @staticmethod
    def dash_to_ham(dash_obj: DASH) -> HAM:
        """ Create a 'HAM' object from the 'DASH' object.

        TODO: write functions to parse for each dash segment type(segment list, segment template, segment base..).

        :param dash_obj:  'DASH' object of the media presentation.
        :type dash_obj: cmafham.models.DASH
        :returns: 'HAM' object for the media presentation.
        :rtype: cmafham.ham.HAM
        """
        # map the presentation here
        selection_sets: list[SelectionSet] = []
        audio_sets: list[SwitchingSet] = []
        text_sets: list[SwitchingSet] = []
        video_sets: list[SwitchingSet] = []
        if dash_obj.mpd:
            # stick to single period for now
            period = dash_obj.mpd.periods[0]
            duration = DashTrackMapper.iso_time(period.duration)
            for a_set in period.adaptation_sets:
                # check segment type...
                for rep in a_set.representations:
                    track = DashTrackMapper.map(a_set, rep, duration)
                    if isinstance(track, AudioTrack):
                        pass
                    if isinstance(track, TextTrack):
                        pass
                    if isinstance(track, VideoTrack):
                        pass
        return HAM(presentation=Presentation(
            id_=gen_uuid(),
            selection_sets=selection_sets
            ),
            dash_obj=dash_obj
        )

    @staticmethod
    def segments_to_ham(base_uri: str = None, segments: list[str] = None) -> HAM:
        """ NOT IMPLEMENTED!
        Create a 'Presentation' from CMAF encoded segments, then return a 'HAM' object from that.

        :param str base_uri: base path location for segments.
        :param segments: list of segment filenames.
        :returns: A 'HAM' object representing the media presentation.
        :rtype: cmafham.ham.HAM
        """
        parsed_files: list[CMAF] = []
        subtitles: list = []
        selection_sets: list[SelectionSet] = []
        audio_sets: list[SwitchingSet] = []
        text_sets: list[SwitchingSet] = []
        video_sets: list[SwitchingSet] = []
        for segment in segments:
            # parse the file data into CMAF components here
            # currently only for single segments.
            if "vtt" in segment:
                # figure out how to parse the subtitle files...
                file_data = CmafSegmentMapper.subtitle(segment)
                if file_data:
                    subtitles.append(file_data)
            else:
                file_data = parse_cmaf_file(base_uri+segment)
                if file_data:
                    parsed_files.append(file_data)
        # evaluate the parsed files and subtitles here...
        return HAM(
            presentation=Presentation(
                id_=gen_uuid(), selection_sets=selection_sets
            )
        )

    @staticmethod
    def ham_manifest(uri: str = None, string: str = None) -> HAM:
        """ Create a HAM object from a saved CMAF 'Presentation' 'manifest' file or string.

        :param str uri: path to the manifest json file.
        :param str string: string representation of the manifest.
        :returns: HAM object for the media presentation.
        :rtype: cmafham.ham.HAM
        """
        if uri:
            with open(uri, "r") as f:
                manifest = json.load(f)
        elif string:
            manifest = json.loads(string)
        else:
            manifest = None
        if not manifest or not manifest.get("presentation"):
            # maybe print/log error, or raise exception..
            return Presentation(id_=gen_uuid(), selection_sets=[])
        manifest = manifest["presentation"]
        # create the 'SelectionSet' objects for the 'Presentation'.
        selection_sets: list[SelectionSet] = []
        for sel_set in manifest.get("selection_sets", []):
            # create the 'SwitchingSet' objects for the 'SelectionSet'.
            switching_sets: list[SwitchingSet] = []
            for sw_set in sel_set.get("switching_sets"):
                # create 'Track' objects for the 'SwitchingSet' first.
                tracks: list = []
                for track in sw_set.get("tracks", []):
                    # create the 'Segment' objects for each track.
                    track["segments"] = [Segment(**s) for s in track.get("segments", [])]
                    if sw_set.get("track_type") == "audio":
                        tracks.append(AudioTrack(**track))
                    if sw_set.get("track_type") == "text":
                        tracks.append(TextTrack(**track))
                    if sw_set.get("track_type") == "video":
                        tracks.append(VideoTrack(**track))
                sw_set["tracks"] = tracks
                switching_sets.append(SwitchingSet(**sw_set))
            sel_set["switching_sets"] = switching_sets
            selection_sets.append(SelectionSet(**sel_set))
        return HAM(
            presentaion=Presentation(
                id_=manifest.get("id", gen_uuid()),
                selection_sets=selection_sets
            )
        )

    @staticmethod
    def ham_to_hls(presentation: Presentation) -> HLS:
        """ Map the properties of a CMAF 'Presentation' to an 'HLS' object.

        :param presentation: CMAF 'Presentation' object for the media presentation.
        :type presentation: cmafham.models.Presentation
        :returns: 'HLS' representation of the CMAF 'Presentation'
        :rtype: cmafham.models.Presentation
        """
        media_tracks: list = []
        video_tracks: list = []
        for sel_set in presentation.selection_sets:
            for sw_set in sel_set.switching_sets:
                if sw_set.tracks:
                    if sw_set.track_type in ("text", "audio"):
                        media_tracks.extend(sw_set.tracks)
                    elif sw_set.track_type == "video":
                        video_tracks.extend(sw_set.tracks)
        media = HlsPresentationMapper.media(media_tracks)
        playlists = HlsPresentationMapper.video(video_tracks, media)
        multivariant = HlsPresentationMapper.manifest(playlists, media)
        return HLS(m3u8_obj=multivariant)

    @staticmethod
    def ham_to_dash(presentation: Presentation) -> DASH:
        """ Map the properties of a CMAF 'Presentation' to a 'DASH' object. """
        return


class HlsTrackMapper:
    """ Class for the mapping of HLS variant stream properties to CMAF 'Track' objects ."""
    @classmethod
    def audio(cls,
              media: Media,
              base_uri: str = "",
              audiolist: M3U8 = None,
              playlists: PlaylistList = None) -> AudioTrack:
        """ Map the properties of 'M3U8' objects to a CMAF 'AudioTrack' object.

        TODO: parse sample rate and bandwidth.

        :param media: HLS EXT-X-MEDIA data.
        :type media: m3u8.model.Media
        :param str base_uri: base uri path for the files, optional.
        :param audiolist: HLS manifest of audio data, optional.
        :type audiolist: m3u8.model.M3U8
        :param playlists: list of variant playlists, optional.
        :type playlists: m3u8.model.PlaylistList
        :returns: CMAF audio track object.
        :rtype: cmafham.models.AudioTrack
        """
        init_seg: str = ""
        segments: list[Segment] = []
        channels = int(media.channels) if media.channels else 0
        duration = cls._duration(audiolist)
        codec = cls._audio_codec(media, playlists)
        if audiolist and audiolist.segment_map:
            # what to do if len of segment_map is > 1
            init_seg = audiolist.segment_map[0].base_uri + audiolist.segment_map[0].uri
        if audiolist and audiolist.segments:
            segments = cls._segment_builder(audiolist.segments, base_uri)
        if not base_uri:
            base_uri = get_path()
        return AudioTrack(
            id_=media.group_id,
            channels=channels,
            codec=codec,
            duration=duration,
            language=media.language,
            segments=segments,
            url_init=init_seg,
            filename=remove_ext(media.uri),
            base_uri=base_uri
        )

    @classmethod
    def text(cls,
             media: Media,
             base_uri: str = "",
             playlist: M3U8 = None) -> TextTrack:
        """ Maps the properties of HLS subtitles to a CMAF 'TextTrack' object.

        :param media: HLS EXT-X-MEDIA data.
        :type media: m3u8.model.Media
        :param str base_uri: base uri path for the files. (optional)
        :param playlist: HLS media playlist. (optional)
        :type playlist: m3u8.model.M3U8
        :returns: CMAF text track object of subtitles.
        :rtype: cmafham.models.TextTrack
        """
        segments: list[Segment] = []
        if playlist and playlist.segments:
            segments = cls._segment_builder(playlist.segments, base_uri)
        duration = cls._duration(playlist)
        if not base_uri:
            base_uri = get_path()
        return TextTrack(
            id_=media.group_id,
            codec=cls._text_codec(media),
            duration=duration,
            language=media.language,
            segments=segments,
            filename=remove_ext(media.uri),
            base_uri=base_uri
        )

    @classmethod
    def video(cls,
              playlist: Playlist,
              base_uri: str = "",
              variant: M3U8 = None) -> VideoTrack:
        """ Map the properties of M3U8 objects to a CMAF 'VideoTrack' object.
        
        :param playlist: variant playlist data from multivariant playlist.
        :type playlist: m3u8.model.Playlist
        :param str base_uri: base uri path for the files. (optional)
        :param variant: HLS media playlist. (optional)
        :type variant: m3u8.model.M3U8
        :returns: CMAF video track object
        :rtype: cmafham.models.VideoTrack
        """
        w, h = 0, 0
        bandwidth = 0
        segments: list[Segment] = []
        duration = cls._duration(variant)
        video_codec = cls._video_codec(playlist.stream_info.codecs)
        fr = float_fr(playlist.stream_info.frame_rate)
        if variant and variant.segments:
            segments = cls._segment_builder(variant.segments, base_uri)
        if playlist.stream_info:
            if len(playlist.stream_info.resolution) == 2:
                w = playlist.stream_info.resolution[0]
                h = playlist.stream_info.resolution[1]
            if playlist.stream_info.bandwidth:
                bandwidth = int(playlist.stream_info.bandwidth)
        if not base_uri:
            base_uri = get_path()
        return VideoTrack(
            id_=gen_uuid(),
            codec=video_codec,
            duration=duration,
            bandwidth=bandwidth,
            segments=segments,
            width=w,
            height=h,
            framerate=fr,
            filename=remove_ext(playlist.uri),
            base_uri=base_uri
        )

    @staticmethod
    def _segment_builder(
            hls_segments: list[HlsSegment],
            base_uri: str = None) -> list[Segment]:
        """ Builds CMAF 'Segment' objects from a list of 'HlsSegment' objects

        :param hls_segments:  list of HLS segments.
        :type hls_segments: list[m3u8.model.Segment]
        :param str base_uri: base uri path for the files. (optional)
        :returns: CMAF 'Segments' for the Track
        :rtype: list[cmafham.models.Segment]
        """
        segments: list[Segment] = []
        for seg in hls_segments:
            if base_uri:
                s_url = seg.base_uri + seg.uri
            else:
                s_url = seg.uri
            duration = seg.duration if seg.duration else 0
            segments.append(
                Segment(
                    filename=seg.uri,
                    duration=duration,
                    url=s_url,
                    byterange=seg.byterange)
            )
        return segments

    @staticmethod
    def _duration(playlist: M3U8) -> float:
        """ Calculate total presentation duration from the segment durations

        :param playlist: HLS media playlist
        :type playlist: m3u8.model.M3U8
        :returns: full media duration
        :rtype: float
        """
        dur_s: float = 0.0
        if playlist.segments:
            for seg in playlist.segments:
                if seg.duration:
                    dur_s += seg.duration
        return dur_s

    @staticmethod
    def _video_codec(codec_string: str) -> str:
        """ Return the video codec """
        codecs = parse_codec(codec_string)
        if codecs:
            for codec in codecs:
                if codec[0] == "video":
                    return codec[1]

    @staticmethod
    def _audio_codec(media: Media, playlists: PlaylistList) -> str:
        """ Parse the codec for the given media by checking the Playlists

        :param media: HLS EXT-X-MEDIA data.
        :type media: m3u8.model.Media
        :param playlists:  list of playlists.
        :type playlists: m3u8.model.PlaylistList
        :returns: the audio codec present if parsed, otherwise empty string
        :rtype: str
        """
        for plist in playlists:
            if not plist.stream_info.codecs or not plist.stream_info.audio:
                continue
            if plist.stream_info.audio == media.group_id:
                codecs = parse_codec(plist.stream_info.codecs)
                if codecs:
                    for codec in codecs:
                        if codec[0] == "audio":
                            return codec[1] 
        return ""

    @staticmethod
    def _text_codec(media: Media) -> str:
        """ Rough determination of caption/subtitle codec 
            **would need to examine segments to determine 608 vs 708

        :param media: HLS EXT-X-MEDIA data.
        :type media: m3u8.model.Media
        :returns: Codec of subtitles, presence of closed captions, or empty string
        :rtype: str
        """
        codec: str = ""
        if media.type == "CLOSED-CAPTIONS" or media.instream_id:
            codec = "embedded"
        elif media.type == "SUBTITLES":
            codec = "wvtt"
        elif media.uri:
            if any(c in media.uri for c in ("m3u8", "vtt")):
                codec = "wvtt"
        return codec


class HlsPresentationMapper:
    """ NOT IMPLEMENTED!
    Class for mapping CMAF 'Presentation' data to an 'HLS' object. """
    @classmethod
    def media(cls,
              tracks: Union[List[AudioTrack], List[TextTrack]]
              ) -> MediaList:
        """ Maps AudioTrack or TextTrack into HLS EXT-X-MEDIA data.

        :param tracks: media track data.
        :type tracks: list[AudioTrack] or list[TextTrack]
        :returns: M3U8 media data
        :rtype: m3u8.model.MediaList
        """
        media_list: MediaList = MediaList()
        for track in tracks:
            if isinstance(track, AudioTrack):
                media_list.append(
                    cls.audio(track)
                )
            if isinstance(track, TextTrack):
                media_list.append(
                    cls.text(track)
                )
        # init the uri attr if not empty
        if len(media_list) > 0:
            media_list.uri()
        return media_list

    @classmethod
    def audio(cls, track: AudioTrack) -> Media:
        """ Create audio 'm3u8.model.Media' objects

        :param track: audio track object
        :type track: cmafham.models.AudioTrack
        :returns: m3u8 media object
        :rtype: m3u8.model.Media

        TODO: possibly set other attr's with defaults, ie. 'default', 'autoselect', 'name'...
        """
        if track.filename:
            filename = track.filename + ".m3u8"
        else:
            filename = track.id + ".m3u8"
        return Media(
            uri=filename,
            type="AUDIO",
            group_id=track.id,
            channels=track.channels,
            language=track.language,
            base_uri=track.base_uri
        )

    @classmethod
    def text(cls, track: TextTrack) -> Media:
        """ Create CLOSED-CAPTION or SUBTITLE 'm3u8.model.Media' objects

        :param track: subtitle/closed caption data
        :type track: cmafham.models.TextTrack
        :returns: subtitle/closed caption media data
        :rtype: m3u8.model.Media
        """
        if track.filename:
            filename = track.filename + ".m3u8"
        else:
            filename = track.id + ".m3u8"
        _type = "CLOSED-CAPTIONS" if track.codec == "embedded" else "SUBTITLES"
        return Media(
            uri=filename,
            type=_type,
            group_id=track.id,
            language=track.language,
            base_uri=track.base_uri
        )

    @classmethod
    def video(cls, tracks: list[VideoTrack], media: MediaList) -> PlaylistList:
        """ Create 'm3u8.model.Playlist' objects for video.

        :param tracks: list of video tracks.
        :type tracks: list[VideoTrack]
        :param media: list of media objects.
        :type media: m3u8.model.MediaList
        :returns: list of variant playlists
        :rtype: m3u8.model.PlaylistList
        """
        playlists: PlaylistList = PlaylistList()
        for track in tracks:
            if track.filename:
                filename = track.filename + ".m3u8"
            else:
                filename = track.id + ".m3u8"
            # create stream_info
            stream_info = None
            for m in media:
                # TODO: need to verify the media matches this playlist...
                if m:    
                    stream_info = cls._stream_info(track, m)
            playlists.append(
                Playlist(
                    uri=filename,
                    stream_info=stream_info,
                    media=media,
                    base_uri=track.base_uri
                )
            )
        return playlists

    @staticmethod
    def _stream_info(track: VideoTrack, track_media: Media) -> StreamInfo:
        """ Create the 'StreamInfo' object for a variant playlist.

        :param track: video track object.
        :type track: cmafham.models.VideoTrack
        :param track_media: variant media object.
        :type track_media: m3u8.model.Media
        :returns: stream info object for the variant playlist.
        :rtype: m3u8.model.StreamInfo

        TODO: need to account for audio/caption media in the input
            (from StreamInfo.__init__)
            bandwidth = kwargs.get("bandwidth")
            closed_captions = kwargs.get("closed_captions")

            # possibly track.id ?
            program_id = kwargs.get("program_id")

            resolution = kwargs.get("resolution")
            codecs = kwargs.get("codecs")
            audio = kwargs.get("audio")
            video = kwargs.get("video")
            subtitles = kwargs.get("subtitles")
            frame_rate = kwargs.get("frame_rate")

            # could parse this from codec?
            video_range = kwargs.get("video_range")
        """
        params: dict = {}
        # media would also determine the
        # audio/subtitles/closed_captions params
        if track.bandwidth:
            params["bandwidth"] = track.bandwidth
        if track.codec:
            # need to parse media to get audio codec..
            params["codecs"] = track.codec
        if track.width and track.height:
            params["resolution"] = (track.width, track.height)
        if track.framerate:
            params["frame_rate"] = track.framerate
        return StreamInfo(**params)

    @classmethod
    def manifest(cls,
                 playlists: PlaylistList,
                 media: MediaList = None) -> M3U8:
        """ Create and assemble the 'm3u8.model.M3U8' for the data.

        TODO: possibly set defaults for version etc.; use 'flag' attrs to determine any other neccesary options could be necesary if coming from dash/ham to enable certain features...

        :param playlists: variant playlists.
        :type playlists: m3u8.model.PlaylistList
        :param media: hls media information.
        :type media: m3u8.model.MediaList
        """
        m3u8_obj = M3U8()
        m3u8_obj.playlists = playlists
        m3u8_obj.media = media
        m3u8_obj.is_variant = True
        # set any other attributes here
        return m3u8_obj

    @classmethod
    def variant(cls,
                track: Union[AudioTrack, TextTrack, VideoTrack],
                playlist: Playlist = None,
                media: Media = None,
                ) -> M3U8:
        """ Create a 'm3u8.model.M3U8' object for media/variant playlist, to create a manifest file...

        :param track: CMAF Track data
        :type track: cmafham.models.AudioTrack or cmafham.models.TextTrack or cmafham.models.VideoTrack
        :param playlist: HLS EXT-X-STREAM-INF data. (optional)
        :type playlist: m3u8.model.Playlist
        :param media: HLS EXT-X-MEDIA data. (optional)
        :type media: m3u8.model.Media
        :returns: media playlist 'M3U8' object.
        :rtype: m3u8.model.M3U8
        """
        variant = M3U8()
        segments: SegmentList = SegmentList()
        if track.segments:
            for seg in track.segments:
                segments.append(cls._segment_builder(seg, track.base_uri))
        if isinstance(track, AudioTrack) and track.url_init:
            variant.segment_map = [InitializationSection(track.url_init)]
        # add other data...
        return variant

    @staticmethod
    def _segment_builder(segment: Segment, base_uri: str = "") -> HlsSegment:
        """ Create the 'HlsSegment's from the 'Segment' data
        
        :param segment:  CMAF segment object
        :type segment: cmafham.models.Segment
        :param str base_uri: base uri path for the files. (optional) 
        :returns: HLS segment object
        :rtype: m3u8.model.Segment

        TODO: need to re-think how to handle this,has to be able to come from dash
              can't re-write segment file names, because only for manifest manipulation at this point...
        """
        if not base_uri:
            base_uri = get_path(segment.url)
        return HlsSegment(
            uri=segment.filename,
            duration=segment.duration,
            base_uri=base_uri,
            byterange=segment.byterange
        )


class DashSegmentParser:
    """ NOT IMPLEMENTED!
    Class to parse data from different types of DASH manifest segment types,
    to return the data in a uniform way for the 'DashTrackMapper' functions.
    """
    @staticmethod
    def base(data1, data2):
        """ Parse segment_base data, format and return.

        :param data1: placeholder parameter.
        :param data2: placeholder parameter.
        """
        return None

    @staticmethod
    def template(data1, data2):
        """ Parse segment_template data, format and return.

        :param data1: placeholder parameter.
        :param data2: placeholder parameter.
        """
        return None

    @staticmethod
    def list(data1, data2):
        """ Parse segment_list data, format and return.

        :param data1: placeholder parameter.
        :param data2: placeholder parameter.
        """
        return None


class DashTrackMapper:
    """ NOT IMPLEMENTED!
    Class for mapping 'MPEGDASH' objects to CMAF 'Track' objects.
    """
    @classmethod
    def map(cls,
            adaptation: AdaptationSet,
            representation: Representation,
            duration: float = None) -> Union[AudioTrack, TextTrack, VideoTrack, None]:
        """ Master track mapping function, determines the type and employs the appropriate mapper and returns the assembled track.

        :param adaptation: adaptation set object.
        :type adaptation: mpegdash.nodes.AdaptationSet
        :param representation: representation object.
        :type representation: mpegdash.nodes.Representation
        :param duration: DASH period duration.
        :returns: CMAF track object if parsed, else None.
        :rtype: AudioTrack or TextTrack or VideoTrack or None
        """
        track_type = cls._track_type(adaptation, representation)
        if track_type == "audio":
            return cls.audio(adaptation, representation, duration)
        if track_type == "text":
            return cls.text(adaptation, representation, duration)
        if track_type == "video":
            return cls.video(adaptation, representation, duration)
        return None

    @classmethod
    def _dash_type(cls, adaptation: AdaptationSet, representation: Representation):
        """ Determine the DASH segment type to parse properly.
        
        :param adaptation: adaptation set object.
        :type adaptation: mpegdash.nodes.AdaptationSet
        :param representation: representation object.
        :type representation: mpegdash.nodes.Representation
        :returns: Nothing yet...
        :rtype: None
        """
        if adaptation.segment_lists:
            return DashSegmentParser.list(adaptation, representation)
        elif adaptation.segment_templates:
            return DashSegmentParser.template(adaptation, representation)
        elif adaptation.segment_bases:
            return DashSegmentParser.base(adaptation, representation)

    @classmethod
    def audio(cls, data1, data2, data3) -> AudioTrack:
        """ Create an 'AudioTrack' from the data.

        :param data1: placeholder parameter.
        :param data2: placeholder parameter.
        :param data3: placeholder parameter.        
        :returns: Audio track object
        :rtype: cmafham.models.AudioTrack
        """
        return AudioTrack()

    @classmethod
    def text(cls, data1, data2, data3) -> TextTrack:
        """ Create an 'TextTrack' from the data.

        :param data1: placeholder parameter.
        :param data2: placeholder parameter.
        :param data3: placeholder parameter.
        :returns: Text track object
        :rtype: cmafham.models.TextTrack
        """
        return TextTrack()

    @classmethod
    def video(cls, data1, data2, data3) -> VideoTrack:
        """ Create an 'VideoTrack' from the data.

        :param data1: placeholder parameter.
        :param data2: placeholder parameter.
        :param data3: placeholder parameter.
        :returns: Video track object
        :rtype: cmafham.models.VideoTrack
        """
        return VideoTrack()

    @classmethod
    def _track_type(cls,
                    adaptation: AdaptationSet,
                    representation: Representation) -> Union[str, None]:
        """
        Use the adaptation set, and representation data to determine the track type.

        :param adaptation:  Adaptation set object.
        :type adaptation: mpegdash.nodes.AdaptationSet
        :param representation: track representation object
        :type representation: mpegdash.nodes.Representation
        :returns: string of the track type ("audio", "text", "video") or None
        :rtype: str | None
        """
        if adaptation.mime_type:
            # parse by mime type..
            return cls._mime_type(adaptation.mime_type)
        if representation.codecs:
            # parse by codec..
            pass
        if representation.audio_sampling_rate:
            # probably wouldnt be in video/text sets?
            return "audio"
        return None

    @staticmethod
    def _segment_builder(
            adaptation: AdaptationSet,
            representation: Representation) -> Union[List[Segment], None]:
        """ Create a CMAF 'Segment' object from an adaptation set and its representation data.

        :param adaptation: adaptation set object.
        :type adaptation: mpegdash.nodes.AdaptationSet
        :param representation:  track representation object.
        :type representation: mpegdash.nodes.Representation
        :returns: CMAF 'Segment's for the presentation if parsed, else None.
        :rtype: list[Segment] | None
        """
        
        return Segment()

    @staticmethod
    def _mime_type(type_str: str) -> str:
        """ Parse the track type from the mime type string.

        TODO:  improve to include parsing of more complex strings.
        
        TODO: return more meaningful data in the future..

        :param str type_str: mime type string.
        :returns: track type string ("audio", "text", "video") or empty string
        :rtype: str
        """
        if "audio" in type_str:
            return "audio"
        if "video" in type_str:
            return "video"
        if any(t in type_str for t in ("text", "application")):
            return "text"
        return ""

    @staticmethod
    def iso_time(time_str: str) -> float:
        """ Return an ISO 8601 time string as a float value in seconds.

        :param str time_str: ISO-8601 formatted time string from DASH manifest ex. ("PT10M34.533S").
        :returns: time as a float value in seconds.
        :rtype: float
        """
        time: float = 0.0
        h = search(r'([\.\,\d]+)H', time_str)
        m = search(r'([\.\,\d]+)M', time_str)
        s = search(r'([\.\,\d]+)S', time_str)
        if h and hasattr(h, "group"):
            hour = float(h.group(1))
            time += (hour * 3600)
        if m and hasattr(m, "group"):
            minute = float(m.group(1))
            time += (minute * 60)
        if s and hasattr(s, "group"):
            sec = float(s.group(1))
            time += sec
        return time


class CmafSegmentMapper:
    """ NOT IMPLEMENTED!
    Class to map CMAF file iso box data into CMAF-HAM model format.
    """
    @classmethod
    def map(cls, data) -> List[SwitchingSet]:
        """ Try to create and return CMAF 'SwitchingSet's for the given data.
        Need to filter the data at this point...
        """
        pass

    @classmethod
    def parse_tracks(cls, data):
        """ Create CMAF 'Track' objects from the file data.
        Need to parse track type to determine the relevant data to parse. """
        pass

    @classmethod
    def create_swset(cls, data):
        """ Create a CMAF 'SwitchingSet' for a set of files.
        Need to split the file box data into some subset of groups before this step most likely.
        """
        pass

    @classmethod
    def subtitle(cls, data):
        """ Parse a single subtitle file? 
        TODO: Think of the best way to handle subtitles here, may need a second function to create the actual track...
        """
        pass
