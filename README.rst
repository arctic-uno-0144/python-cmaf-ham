CmafHam
=======

Python implementation of an HLS/DASH parser for CMAF encoded files, based on the `CMAF`_ Hypothetical Application Model(ISO/IEC 23000-19).

Inspired by the MonteVideo Summer Camp `project`_ for the Common Media Library.

Credit to the `m3u8`_ and `mpegdash`_ libraries for parsing and rendering.


TODO: improve and include more details, use cases, limitations, etc.

TODO: create tests...


Documentation
=============

Loading from a manifest
-----------------------

To load a HLS or DASH manifest from a uri/url use the `load` function.

.. code-block:: python
    
    import cmafham

    hls_url = "http://videoserver.com/manifest.m3u8"
    # could also use local file "/path/to/manifest.m3u8"
    ham_obj = cmafham.load(hls_url)
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

This project is still in a very early stage of development and is subject to change frequently.

Due to the natural limitations of the interoperability of DASH and HLS there are some features and attributes that will be lost in the process. Especially features such as encryption, which are not covered in the CMAF spec.

List of known limitations:
    * Parsing HLS or DASH from strings
    * DASH parsing or rendering.
    * Fully rendering to HLS.
    * Parsing of all attributes from HLS.

.. _CMAF: https://mpeg.chiariglione.org/standards/mpeg-a/common-media-application-format/text-isoiec-cd-23000-19-common-media-application
.. _m3u8: https://github.com/globocom/m3u8
.. _mpegdash: https://github.com/sangwonl/python-mpegdash/tree/master
.. _cta: https://cdn.cta.tech/cta/media/media/resources/standards/cta-5005-a-final.pdf
.. _project: https://github.com/qualabs/common-media-library/tree/feature/cmaf-ham
