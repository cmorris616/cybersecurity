def get_url_variations(base_url: str) -> []:
    """
    Returns a list of variations on the provided url (i.e. http, https, www)
    :param base_url: the base url from which to create variations
    :return: a list of varied urls
    """
    if '://' in base_url:
        base_url = base_url[base_url.index('://') + 3:]

    if base_url.startswith('www.'):
        base_url = base_url[4:]

    url_list = [
        base_url,
        'http://' + base_url,
        'https://' + base_url,
        'http://www.' + base_url,
        'https://www.' + base_url,
    ]

    return url_list
