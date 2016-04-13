from functools import partial

from .read_html_simple import fetch_paths
from .sync_media_function import make_rsync_command


def sync(subfolder):
    return make_rsync_command(subfolder,
                              local_media_path="/www/beta4/live/assets/media")


output_path = "./synctools/output/beta-rsync-commands.txt"

def write_to_output(iterator):
    with open(output_path, 'w') as out_file:
        for line in iterator:
            out_file.write(line+"\n")

make_commands = fetch_paths >> partial(map, sync)
executor = make_commands >> write_to_output  # Side-effects! Impure! Impure!



def main(location):
    """ Pull down all images referenced in a given HTML URL or file."""

    
    print()
    print("make_commands:", type(make_commands), make_commands)
    print()
    import ipdb
    ipdb.set_trace()
    print()
    

    return executor(location)

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
