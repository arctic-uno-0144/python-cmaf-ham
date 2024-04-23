CmafHam
=======

Python implementation of a HLS/DASH parser for CMAF encoded files, based on the CMAF Hypothetical Application Model(ISO/IEC 23000-19).

TODO: include more details, and use cases.
TODO: include credits to the summer camp, and the parsing libraries

Documentation
=============

Loading from a manifest
-----------------------

To load a HLS or DASH manifest from a uri/url use the `load` function.

.. code-block:: python
    import cmafham

    hls_uri = "/path/to/manifest.m3u8"
    hls_url = "http://videoserver.com/manifest.m3u8"
    ham_obj = cmafham.load(hls_uri)
    # this creates the 'HAM' object
    # that contains the all three object representations of the media
    print(ham_obj.__dict__)

Creating manifest files
-----------------------

.. code-block:: python
    import cmafham

    ham_obj = cmafham.load("http://videoserver.com/manifest.m3u8")

    # Create manifest files for an HLS presentation.
    ham_obj.render_hls()
    
    # Create manifest file for a DASH presentation.
    ham_obj.render_dash()


Limitations
===========

This project is still in a very early development stage.

List of known limitations:
- parsing from strings
- parsing or rendering to DASH
- fully rendering to HLS
- parsing of all attributes from HLS
