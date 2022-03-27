from ploomber.cloud import api


def download_data(key):
    """

    Examples
    --------
    >>> from ploomber.cloud import download_data
    >>> download_data('v2.mov')
    """
    url = api.download_data(key).text
    api._download_file(url)
