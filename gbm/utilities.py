import os


def get_preferences_dir(make_dir=True):
    """
    Get the preferences directory, if the make_dir parameter is True
    then try to create the directory if it doesn't exists.

    The directory is created at $HOME/.gbm or wherever the envvar
    GBM_PREFERENCES_DIR is set to.
    """
    directory = os.environ.get(
        'GBM_PREFERENCES_DIR', os.environ['HOME'] + '/.gbm')
    if make_dir and not os.path.exists(directory):
        os.mkdir(directory)
    return directory
