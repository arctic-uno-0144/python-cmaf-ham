""" CMAF-HAM models """


class Segment:
    """ CMAF SEGMENT OBJECT """
    def __init__(self,
                 duration: float | int = 0.0,
                 url: str = "",
                 byterange: str = None
                 ) -> None:
        self.duration = float(duration)
        self.url = url
        self.byterange = byterange


class AudioTrack:
    """ CMAF AUDIO TRACK """
    def __init__(self,
                 id_: str = "",
                 codec: str = "",
                 channels: int = 0,
                 duration: float | int = 0.0,
                 language: str = "",
                 segments: list[Segment] = None,
                 sample_rate: float | int = 0.0,
                 bandwidth: int = 0,
                 url_init: str = ""
                 ) -> None:
        self.id_ = id_
        self.codec = codec
        self.duration = float(duration)
        self.language = language
        self.segments = segments
        self.sample_rate = sample_rate
        self.channels = channels
        self.bandwidth = bandwidth
        self.url_init = url_init


class TextTrack:
    """ CMAF TEXT TRACK """
    def __init__(self,
                 id_: str = "",
                 codec: str = "",
                 duration: float | int = 0.0,
                 language: str = "",
                 segments: list[Segment] = None
                 ) -> None:
        self.id_ = id_
        self.codec = codec
        self.duration = float(duration)
        self.language = language
        self.segments = segments


class VideoTrack:
    """ CMAF VIDEO TRACK """
    def __init__(self,
                 id_: str = "",
                 codec: str = "",
                 duration: float | int = 0.0,
                 language: str = "",
                 bandwidth: int = 0,
                 segments: list[Segment] = None,
                 width: int = 0,
                 height: int = 0,
                 framerate: float | int = 0.0,
                 par: str = "",
                 sar: str = "",
                 scan_type: str = ""
                 ) -> None:
        self.id_ = id_
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


class SwitchingSet:
    """ CMAF SWITCHING SET """
    def __init__(self,
                 id_: str = "",
                 tracks: list[AudioTrack | VideoTrack | TextTrack] = None
                 ) -> None:
        self.id_ = id_
        self.tracks = tracks


class SelectionSet:
    """ CMAF SELECTION SET """
    def __init__(self,
                 id_: str = "",
                 switching_set: SwitchingSet = None
                 ) -> None:
        self.id_ = id_
        self.switching_set = switching_set


class Presentation:
    """ CMAF PRESENTATION """
    def __init__(self,
                 id_: str = "",
                 selection_sets: list[SelectionSet] = None
                 ) -> None:
        self.id = id_
        self.selection_sets = selection_sets
