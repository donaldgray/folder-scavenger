import os

SLEEP_SECONDS = int(os.environ.get('SLEEP_SECONDS'))
ROOT_FOLDER = os.environ.get('ROOT_FOLDER')

if "MINIMUM_AGE" in os.environ:
    MINIMUM_AGE = int(os.environ.get('MINIMUM_AGE'))
else:
    MINIMUM_AGE = 0

if "DELETE_LEAF_CONTENTS" in os.environ:
    DELETE_LEAF_CONTENTS = bool(os.environ.get('DELETE_LEAF_CONTENTS'))
else:
    DELETE_LEAF_CONTENTS = False
