def number_to_ordinal(nnn):
    if 10 <= nnn % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(nnn % 10, 'th')
    return "{}{}".format(nnn, suffix)
