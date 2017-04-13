def xx():
    return 1, (2, 3)


def us(*args):
    print args

xs = xx()
us(xs[0], *(xs[1]))
