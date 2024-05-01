CmafHam is a Python implementation of an `HLS`_/`DASH`_ parser for `CMAF`_ encoded files, based on the CMAF 'Hypothetical Application Model' (ISO/IEC 23000-19 Chapter 6) and the `DASH HLS Interoperability Specification`_ (CTA-5005-A).

Inspired by the `2024 MonteVideo Tech Summer Camp`_ CMAF-HAM `project`_ for the `Common Media Library`_.

Input manifests are parsed and mapped into CMAF 'HAM' model objects, where the data can be stored manifest agnostic and can be manipulated or renderead to manifest(s) for either HLS or DASH.

This project also has the goal of generating a HAM model object solely from CMAF encoded segment files without a manifest.

Credit to the `m3u8`_ and `mpegdash`_ libraries used for parsing and rendering of HLS and DASH, and the `mp4analyser`_ library for the `ISOBMFF box`_ parsing.

TODO: improve docs, create tests...


Limitations
===========

This project is still in a very early stage of development and is subject to change frequently.

Due to the limitations of the `interoperability`_ between DASH and HLS there are some features and attributes that cannot currently be presereved in the process. Especially features that are unique to either HLS or DASH, or those which are not covered by the CMAF specification.

List of known limitations:
    * DASH Parsing.                             **[NOT SUPPORTED]**
    * Parsing of HLS or DASH from strings.      **[NOT SUPPORTED]**
    * Parsing from raw segment files.           **[NOT SUPPORTED]**
    * Full rendering to HLS.                    **[NOT SUPPORTED]**


Documentation
=============

Loading from a manifest file
----------------------------

To create a 'HAM' object from an HLS or DASH manifest file use the ``load`` function.

.. code-block:: python
    
    import cmafham

    # from a web url
    hls = "http://videoserver.com/manifest.m3u8"
    ham_obj = cmafham.load(hls)

    # from a local file
    hls = "/path/to/manifest.m3u8"
    ham_obj = cmafham.load(hls)


This parses the input manifest and attempts to create a ``cmafham.ham.HAM`` object containing the ``cmafham.models.Presentation``, ``cmafham.models.HLS``, ``cmafham.models.DASH`` objects that describe the media presentation. These objects give you access to the media's properties, as well as the manifest for each presentaion format (HLS, DASH, \*\*CMAF).

The properties can be accessed via the ``presentation``, ``hls``, and ``dash`` attributes.

The ``hls`` attribute is a container object (``cmafham.models.HLS``) consisting of the `M3U8 object`_ and the HLS manifest as a string.

The ``dash`` attribute is a container object (``cmafham.models.DASH``) consisting of the `MPEGDASH object`_ and the DASH manifest as a string.

The ``presentation`` attribute contains the `Presentation object`_.

.. code-block:: python

    # the 'm3u8.model.M3U8' object of the HLS representation.
    print(type(ham_obj.hls.m3u8))
    # the HLS manifest as a string
    print(ham_obj.hls.manifest)

    # the 'mpegdash.nodes.MPEGDASH' object of the DASH representation.
    print(type(ham_obj.dash.mpd))
    # the DASH manifest as a string
    print(ham_obj.dash.manifest)

    # the 'cmafham.models.Presentation' object.
    print(type(ham_obj.presentation))
    # 'Presentation' object formatted to a string
    print(ham_obj.presentation.manifest)


Creating manifest files
-----------------------

.. code-block:: python
    
    import cmafham

    ham_obj = cmafham.load("http://videoserver.com/manifest.m3u8")

    # Create manifest files for an HLS presentation.
    ham_obj.render_hls()
    
    # Create manifest file for a DASH presentation.
    ham_obj.render_dash()

    # Create a json file of a CMAF-HAM presentation.
    ham_obj.render_ham()


``** "HAM manifest" files can be imported/exported in JSON format.``

For example:
    .. code-block:: javascript

        {
          "ham_version": "0.0.1",
          "presentation": {
            "id": "f513b96c-3be4-4337-acb5-5414ab2a513f",
            "selection_sets": [
              {
                "id": "befb6403-6832-491d-a68c-ce4f15a83a6a",
                "switching_sets": [
                  {
                    "id": "f0618e96-3e6d-4aeb-8bc0-e55c915847d8",
                    "track_type": "video",
                    "tracks": [
                      {
                        "id": "3a93fa61-d38d-4b62-9cbb-e76e4e10926f",
                        "codec": "avc1.640028",
                        "duration": 635.0,
                        "language": "",
                        "bandwidth": 10377445,
                        "segments": [
                          {
                            "filename": "bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Avc_16x9_Sdr_1920x1080p_30Hz_10000Kbps_Cbr_000000001.cmfv",
                            "duration": 30.0,
                            "url": "/docs/examples/hls/example-1/bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Avc_16x9_Sdr_1920x1080p_30Hz_10000Kbps_Cbr_000000001.cmfv",
                            "byterange": null
                          }
                        ],
                        "width": 1920,
                        "height": 1080,
                        "framerate": 29.97,
                        "par": "",
                        "sar": "",
                        "scan_type": "",
                        "filename": "bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Avc_16x9_Sdr_1920x1080p_30Hz_10000Kbps_Cbr",
                        "base_uri": "/docs/examples/hls/example-1/"
                      }
                    ]
                  }
                ]
              },
              {
                "id": "36c1db6e-bfa7-4737-9315-5524d702e22a",
                "switching_sets": [
                  {
                    "id": "program_audio_0",
                    "track_type": "audio",
                    "tracks": [
                      {
                        "id": "program_audio_0",
                        "codec": "avc1.640028",
                        "duration": 635.0,
                        "language": "und",
                        "segments": [
                          {
                            "filename": "bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Aac_He_96Kbps_000000001.cmfa",
                            "duration": 30.0,
                            "url": "/docs/examples/hls/example-1/bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Aac_He_96Kbps_000000001.cmfa",
                            "byterange": null
                          }
                        ],
                        "sample_rate": 0.0,
                        "channels": 0,
                        "bandwidth": 0,
                        "url_init": "/docs/examples/hls/example-1/bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Aac_He_96Kbpsinit.cmfa",
                        "filename": "bbb_sunflower_1080p_30fps_normal_Ott_Cmaf_Cmfc_Aac_He_96Kbps",
                        "base_uri": "/docs/examples/hls/example-1/"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        }

.. _HLS: https://tools.ietf.org/html/draft-pantos-hls-rfc8216bis
.. _DASH: https://dashif.org/guidelines/iop-v5/
.. _CMAF: https://mpeg.chiariglione.org/standards/mpeg-a/common-media-application-format/text-isoiec-cd-23000-19-common-media-application
.. _DASH HLS Interoperability Specification: https://cdn.cta.tech/cta/media/media/resources/standards/cta-5005-a-final.pdf
.. _interoperability: https://cdn.cta.tech/cta/media/media/resources/standards/cta-5005-a-final.pdf
.. _2024 MonteVideo Tech Summer Camp: https://www.youtube.com/playlist?list=PLfXb5yywZ6rd0TKFZXNe-BUv22aMH5eGp
.. _project: https://github.com/qualabs/common-media-library/tree/feature/cmaf-ham
.. _Common Media Library: https://github.com/streaming-video-technology-alliance/common-media-library
.. _m3u8: https://github.com/globocom/m3u8
.. _mpegdash: https://github.com/sangwonl/python-mpegdash/tree/master
.. _mp4analyser: https://github.com/essential61/mp4analyser/tree/master
.. _ISOBMFF box: https://www.loc.gov/preservation/digital/formats/fdd/fdd000079.shtml
.. _M3U8 object: https://github.com/globocom/m3u8/blob/3c352ffd738cfa630c11a6920a9fbc605fc2a047/m3u8/model.py#L23
.. _MPEGDASH object: https://github.com/sangwonl/python-mpegdash/blob/a9f5e78f6400328e269f655e5df45e37d990a6e3/mpegdash/nodes.py#L737
.. _Presentation object: /Users/sreese/Documents/Personal/code/python_cmafham/docs/_build/html/cmafham.html#cmafham.models.Presentation