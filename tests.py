"""
CmafHam tests
"""
import cmafham
import json


TEST_PATH = "/Users/sreese/documents/personal/code/" \
            "python_cmafham/docs/examples"
FILE_MANIFEST = TEST_PATH + "/hls/example-1/bbb_sunflower_1080p_30fps_normal.m3u8"


def print_json(to_dump):
    """ Dump an object to json and print it """
    if isinstance(to_dump, dict):
        print(json.dumps(to_dump, indent=2, default=str))
    elif isinstance(to_dump, str):
        temp = json.loads(to_dump)
        print(json.dumps(temp, indent=2, default=str))
    elif hasattr(to_dump, "__dict__"):
        try:
            print(json.dumps(to_dump.__dict__, indent=2, default=str))
        except AttributeError:
            print(json.dumps(dir(to_dump), indent=2, default=str))
    else:
        print(str(to_dump))


def main(manifest):
    """ Main testing funciton """
    ham = cmafham.load(manifest)
    # ham.render_ham("/Users/sreese/documents/personal/code/python_cmafham/docs/examples/ham/")
    print_json(ham.presentation.manifest)
    # for sel in ham.presentation.selection_sets:
    #     print("Selection Sets Found!")
    #     for sw in sel.switching_sets:
    #         print("Switching Set Found!")
    #         print(type(sw))
            # print_json(sw)
            # for tr in sw.tracks:
            #     print("Track Found!")
            #     print_json(tr)
            #     for s in sw.tracks.segments:
            #         print("Segment Found!")
            #         print_json(s)


if __name__ == '__main__':
    main(FILE_MANIFEST)
