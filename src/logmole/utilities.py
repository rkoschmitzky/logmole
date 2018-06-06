def chunks(iterable, n):
    """ Yield successive n-sized chunks from an iterable."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]
