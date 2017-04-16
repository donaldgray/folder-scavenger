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
    #   while subfolders exist at path:
    #       descend at random
    #   else:
    #     os.removedirs(path)

    while True:

        path = settings.ROOT_FOLDER

        keep_going = True

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

                if settings.MINIMUM_AGE > 0:
                    age = time.time() - os.stat(path).st_mtime
                    console_log('file age is %d' % age)

                    if age > settings.MINIMUM_AGE:
                        console_log('file age %d greater than threshold %d'
                                    % (str(age), str(settings.MINIMUM_AGE)))
                        attempt_delete = False
                    else:
                        console_log('file age %d less than threshold %d'
                                    % (str(age), str(settings.MINIMUM_AGE)))

                if attempt_delete:
                    console_log('removedirs at %s' %path)
                    try:
                        os.removedirs(path)
                    except OSError as os_exception:
                        console_log('removedirs failed: %s' % str(os_exception))

        console_log('sleeping for ' + str(settings.SLEEP_SECONDS) + ' second(s)')
        time.sleep(int(settings.SLEEP_SECONDS))

def console_log(message):

    """ example docstring """
    print('{:%Y%m%d %H:%M:%S} '.format(datetime.datetime.now()) + message)

if __name__ == "__main__":
    main()
