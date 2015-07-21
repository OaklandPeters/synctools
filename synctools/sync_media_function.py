#!/Users/opeters/workspace/Atlantic-CMS/bin/python
"""
A simple script I wrote because I can never remember the
exact syntax of the rsync args.
Useage:

rsync-media img/mt/2014/09

Which you can copy paste from the error message that will 
make you want to rsync.



------------------------
Oakland's Bug Report: on 2014/04/21
For me, running this script from: /Users/opeters/workspace/Atlantic-CMS
>>> python bin/sync-media.py img/citylab/2015/
Looses the outermost directory. IE:
  remote directory: img/citylab/2015/01/{*}
Writes to:
  local directory:  img/citylab/2015/{*}
But should write to:
  local direcotyr:  img/citylab/2015/01/{*}
-------------------

Updating a few things:
- changing calculation of local_path:
    - Uses os.path.join - to prevent bug if you forget to include trailing '/' on subfolder (when entered from commandline)
    - Does not append "..", because it creates a problem when rooting at a higher level (eg img/2015 )
        - ? Does the new form work with subfolders like: img/2015/02/ ? 
- ATLCMS: changed path calculations - so it is OS independent (basically no direct reference to '/')
- Creating parent directories: now can create more than the topmost directory.
"""
import os, sys

#ATLCMS = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "Atlantic-CMS"))
ATLCMS_PATH = "/Users/opeters/workspace/Atlantic-CMS"
LOCAL_MEDIA_PATH = os.path.join(ATLCMS_PATH, "assets", "media")

def sync_media(subfolder):
    """
    """
    if ".." in subfolder:
        raise ValueError("Subfolder should not contain '..'")
    elif subfolder[0] == os.path.sep:
        raise ValueError("Subfolder should not be an absolute path (~begins with '/').")

    remote_path = os.path.join("/www/cmsprod/shared/assets/media/", subfolder)
    local_path = os.path.realpath(os.path.join(LOCAL_MEDIA_PATH, subfolder, '..'))

    def partial_paths(base, folder):
        parts = [part for part in folder.split(os.path.sep) if part]
        for i in range(len(parts)):
            yield os.path.join(base, *parts[0:(i+1)])

    # Create any parent directories that need to exist
    for path in partial_paths(LOCAL_MEDIA_PATH, subfolder):
        if not os.path.exists(path):
            os.makedirs(path)

    command = "rsync -avz proxy1.atlprod.amc:%(remote_path)s %(local_path)s" % {
        "remote_path": remote_path,
        "local_path": local_path,
    }

    print(command)
    os.system(command)
