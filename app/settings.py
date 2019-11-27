import os
import distutils.util

DEBUG = bool(distutils.util.strtobool(os.getenv("DEBUG", "True")))
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", default="1"))
ROOT_FOLDER = os.getenv("ROOT_FOLDER")
MINIMUM_AGE = int(os.getenv("MINIMUM_AGE", default="0"))
DELETE_LEAF_CONTENTS = bool(distutils.util.strtobool(os.getenv("DELETE_LEAF_CONTENTS", default="False")))
FREE_SPACE_THRESHOLD = int(os.getenv("FREE_SPACE_THRESHOLD", default="100"))
USE_INODES = bool(distutils.util.strtobool(os.getenv("USE_INODES", default="False")))
CHECK_FILE_AGE = bool(distutils.util.strtobool(os.getenv("CHECK_FILE_AGE", default="False")))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", default=None)
WAIT_FOR_ROOT_TO_EXIST = bool(distutils.util.strtobool(os.getenv("WAIT_FOR_ROOT_TO_EXIST", default="False")))
PROCESS_INDIVIDUAL_FILES = bool(distutils.util.strtobool(os.getenv("PROCESS_INDIVIDUAL_FILES", default="False")))
