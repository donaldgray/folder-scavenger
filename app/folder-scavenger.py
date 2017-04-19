import os
import sys
import time
import random
import string
import datetime
import settings
import random

def main():
    console_log('scavenger starting')

    # can't hold all the tree in memory at once,
    # so pick an item from the root on each cycle

    # loop:
    #   if free space > threshold:
    #       next
    #   path = root
    #   loop:
    #       if subfolders exist at path:
    #           pick a randon descendant
    #           add to path
    #           next
    #
    #       if age of deepest subfolder is < minimum age:
    #           next (will quit inner loop)
    #
    #       if flag set to delete leaf contents:
    #           remove all files in deepest subfolder
    #
    #       os.removedirs(path)

    while True:

        path = settings.ROOT_FOLDER

        keep_going = True

        free_space_percentage = get_free_space(path)
        console_log('free space = %d%%' % free_space_percentage)

        if free_space_percentage > settings.FREE_SPACE_THRESHOLD:
            console_log('free space greater than threshold (%d%%)'
                        % settings.FREE_SPACE_THRESHOLD)
            keep_going = False

        while keep_going:
            subfolders = [os.path.join(path, o)
                          for o in os.listdir(path)
                          if os.path.isdir(os.path.join(path, o))]

            if len(subfolders) > 0:
                path = random.choice(subfolders)
                console_log('descending to %s' % path)
            else:
                console_log('no more subfolders')
                keep_going = False

                attempt_delete = True

                if path == settings.ROOT_FOLDER:
                    console_log('this is the root, so we stop here.')
                    attempt_delete = False
                    continue

                if settings.MINIMUM_AGE > 0:
                    age = time.time() - os.stat(path).st_mtime
                    console_log('file age is %d' % age)

                    if age < settings.MINIMUM_AGE:
                        console_log('file age %d less than threshold %d'
                                    % (age, settings.MINIMUM_AGE))
                        attempt_delete = False
                    else:
                        console_log('file age %d greater than threshold %d'
                                    % (age, settings.MINIMUM_AGE))

                if attempt_delete:
                    if settings.DELETE_LEAF_CONTENTS:
                        files = [os.path.join(path, o)
                                 for o in os.listdir(path)
                                 if os.path.isfile(os.path.join(path, o))]

                        if len(files) > 0:
                            for file in files:
                                console_log('removing %s' % file)
                                os.remove(file)

                    console_log('removedirs at %s' %path)
                    try:
                        os.removedirs(path)
                    except OSError as os_exception:
                        console_log('removedirs failed: %s' % str(os_exception))

        console_log('sleeping for %s second(s)' % settings.SLEEP_SECONDS)
        time.sleep(settings.SLEEP_SECONDS)

def get_free_space(pathname):
    st = os.statvfs(pathname)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = st.f_frsize * (st.f_blocks - st.f_bfree)
    if total > 0:
        return 100 - (100 * (float(used) / total))

    return 100

def console_log(message):

    """ example docstring """
    print('{:%Y%m%d %H:%M:%S} '.format(datetime.datetime.now()) + message)

if __name__ == "__main__":
    main()
