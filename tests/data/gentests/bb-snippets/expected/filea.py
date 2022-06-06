# [[start sumfn
def sum(a, b):
    return a + b
# end]]


def something_else():
    """not sure what this does"""
    a = 1
    # [[start something_else_middle
    a += 100
    a += 1000
    # end]]
    b = 2
    return b + a
