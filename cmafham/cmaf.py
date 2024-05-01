"""
NOT IMPLEMENTED!
This module parses CMAF encoded files for mapping to a CMAF Presentation.

:copyright: (c) 2024 Shayne Reese.
:license: MIT, see LICENSE for more details.
"""

from mp4analyser.iso import Mp4File


class CmafInitSegment:
    """ NOT IMPLEMENTED!
    Container for CMAF initilization segment files. 
    
    TODO: try to group the content files here as well.
    """
    def __init__(self):
        pass


class CmafMediaSegment:
    """ NOT IMPLEMENTED!
    Container for CMAF media files.
    
    TODO: extract meaningful data, how to match with an init segment..
    """
    def __init__(self):
        pass


class CMAF:
    """ NOT IMPLEMENTED!
    Core container for CMAF file box data.
    
    TODO: Needs to be flexible for file type, and data types, etc.
    
    * init files contain more attribute data
    * classify between init or media
    * need to find a way to group media files within their init file group...
    """
    def __init__(self):
        pass


class BoxParser:
    """ NOT IMPLEMENTED!
    Class for Parsing ISOBMFF boxes, returns any relevant data.
    """
    @classmethod
    def parse(cls, box) -> dict:
        """ Parse the box by using the parser for its type. """
        fn_map = {
            "unsupported": cls._unsupported,
            "moov": cls._moov
        }
        parser = fn_map.get(box.header.type, "unsupported")
        return parser(box)
    
    @staticmethod
    def _unsupported(box):
        """ Default parser for unsupported box types. """
        return {}

    @staticmethod
    def _moov(box):
        """ Parser for 'moov' boxes. """
        return {}


def parse_children(box) -> dict:
    """ NOT IMPLEMENTED!
    Parse a box and all of it's child boxes, return the extracted data as a dict for further parsing/analysis.
    
    TODO: think of how to best handle/present the return data.
    """
    data: dict = {}
    if hasattr(box, "child_boxes"):
        for child in box.child_boxes:
            # do something
            data.update(BoxParser.parse(child))
            if hasattr(child, "child_boxes"):
                # do something with data
                data.update(parse_children(child))
    return data


def parse_cmaf_file(filename: str):
    """ NOT IMPLEMENTED! 
    
    TODO: Think of the best way to do this, seems like the init files will be the only way to get the properties right.
    
    TODO: work on getting the proper files aligned with the init file, probably parse all files, and then create a function to add matching content objects to an init object...
    """
    valid_types = ("mp4", "fmp4", "cmfv", "cmfa")
    if any(t in filename for t in valid_types):
        mp4 = Mp4File(filename)
        for box in mp4.child_boxes:
            parse_children(box)
