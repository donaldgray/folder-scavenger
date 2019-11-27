import signal
import os
import sys
import time
import random
import string
import datetime
import settings
import random
import requests
import logging
import logzero
from logzero import logger

requested_to_quit = False

def slack_announce(message):
    if settings.SLACK_WEBHOOK_URL is not None:
        _ = requests.post(settings.SLACK_WEBHOOK_URL, json={"text": message, "link_names": 1})


def announce_error(message):
    logger.error(message)
    slack_announce(f"scavenger: {message}")


def announce(message):
    logger.info(message)
    slack_announce(f"scavenger: {message}")


def main():
    logger.info("starting")

    announce(f"{settings.ROOT_FOLDER} starting")

    setup_signal_handling()

    # can't hold all the tree in memory at once,
    # so pick an item from the root on each cycle

    # loop:
    #   while subfolders exist at path:
    #       descend at random
    #   else:
    #     os.removedirs(path)

    if settings.WAIT_FOR_ROOT_TO_EXIST:
        logger.info("waiting for root folder to exist")
        while not os.path.isdir(settings.ROOT_FOLDER):
            logger.info(f"root folder not present, sleeping for {settings.SLEEP_SECONDS} seconds")
            time.sleep(settings.SLEEP_SECONDS)
        logger.info("root folder exists")

    while not requested_to_quit:

        path = settings.ROOT_FOLDER

        keep_going = True

        free_space_percentage = get_free_space(path)
        logger.info(f"free space = {free_space_percentage}%")

        if settings.USE_INODES:
            logger.info("(based on number of free inodes)")

        if free_space_percentage > settings.FREE_SPACE_THRESHOLD:
            logger.info(f"free space greater than threshold ({settings.FREE_SPACE_THRESHOLD}%)")

            keep_going = False

        while keep_going:
            try:
                subfolders = [os.path.join(path, o)
                            for o in os.listdir(path)
                            if os.path.isdir(os.path.join(path, o))]
            except OSError as os_exception:
                announce_error(f"problem during fetch of subfolders: {os_exception}")
                keep_going = False
                continue

            if len(subfolders) > 0:
                path = random.choice(subfolders)
                logger.info(f"descending to {path}")
            else:
                logger.info("no more subfolders")
                keep_going = False

                attempt_delete = True

                if path == settings.ROOT_FOLDER:
                    logger.info("this is the root, so we stop here.")
                    attempt_delete = False
                    continue

                if settings.CHECK_FILE_AGE:
                    logger.info("using CHECK_FILE_AGE strategy")

                    try:
                        files = [os.path.join(path, o)
                                for o in os.listdir(path)
                                if os.path.isfile(os.path.join(path, o))]
                    except OSError as os_exception:
                        announce_error(f"problem during fetch of files: {os_exception}")
                        keep_going = False
                        continue

                    if len(files) == 0:
                        logger.info("leaf has no contents - will check minimum age of path later")
                    else:
                        for file in files:
                            age = 0
                            try:
                                age = int(time.time() - os.stat(file).st_mtime)
                            except FileNotFoundError as fnf_exception:
                                announce_error(f"os.stat on {file} failed: {fnf_exception}")
                                break

                            if age < settings.MINIMUM_AGE:
                                logger.info(f"found file {file} at age {age} less than threshold {settings.MINIMUM_AGE}, so will not attempt delete")
                                attempt_delete = False
                                break

                if attempt_delete and settings.PROCESS_INDIVIDUAL_FILES:
                    logger.info("using process-individual-files strategy")
                    try:
                        files = [os.path.join(path, o)
                                for o in os.listdir(path)
                                if os.path.isfile(os.path.join(path, o))]
                    except OSError as os_exception:
                        announce_error(f"problem during fetch of files: {os_exception}")
                        keep_going = False
                        continue

                    if len(files) == 0:
                        logger.info("leaf has no contents - will check minimum age of path later")
                    else:
                        for file in files:
                            age = 0
                            try:
                                age = int(time.time() - os.stat(file).st_mtime)
                            except FileNotFoundError as fnf_exception:
                                announce_error(f"os.stat on {file} failed: {fnf_exception}")
                                break

                            if age > settings.MINIMUM_AGE:
                                logger.info(f"removing file {file} as age {age} greater than threshold {settings.MINIMUM_AGE}")
                                try:
                                    os.remove(file)
                                except FileNotFoundError as fnf_exception:
                                    announce_error(f"os.remove on {file} failed: {fnf_exception}")
                                    break
                    attempt_delete = False

                else if attempt_delete and settings.MINIMUM_AGE > 0:
                    logger.info("using normal path-age strategy")
                    age = int(time.time() - os.stat(path).st_mtime)
                    logger.debug(f"path age is {age}")

                    if age < settings.MINIMUM_AGE:
                        logger.info(f"path age {age} less than threshold {settings.MINIMUM_AGE}")
                        attempt_delete = False
                    else:
                        logger.info(f"path age {age} greater than threshold {settings.MINIMUM_AGE}")

                if attempt_delete:
                    if settings.DELETE_LEAF_CONTENTS:
                        files = [os.path.join(path, o)
                                 for o in os.listdir(path)
                                 if os.path.isfile(os.path.join(path, o))]

                        if len(files) > 0:
                            for file in files:
                                logger.info(f"removing {file}")
                                os.remove(file)

                    logger.info(f"removedirs at {path}")
                    try:
                        os.removedirs(path)
                    except OSError as os_exception:
                        announce_error(f"removedirs failed: {os_exception}")

        logger.info(f"sleeping for {settings.SLEEP_SECONDS} second(s)")
        time.sleep(settings.SLEEP_SECONDS)


def signal_handler(signum, frame):
    logger.info(f"Caught signal {signum}")
    global requested_to_quit
    requested_to_quit = True


def setup_signal_handling():
    logger.info("setting up signal handling")
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def get_free_space(pathname):
    st = os.statvfs(pathname)

    if settings.USE_INODES:
        free = st.f_favail
        total = st.f_files
        used = total-free
    else:
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = st.f_frsize * (st.f_blocks - st.f_bfree)

    if total > 0:
        return 100 - (100 * (float(used) / total))

    return 100


if __name__ == "__main__":
    if settings.DEBUG:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    main()
