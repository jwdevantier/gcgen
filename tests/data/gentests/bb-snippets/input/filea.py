# <<? sumfn ?>>
def sum(a, b):
    return a + b
# <<? /sumfn ?>>


def something_else():
    """not sure what this does"""
    a = 1
    # <<? something_else_middle ?>>
    a += 100
    a += 1000
    # <<? /something_else_middle ?>>
    b = 2
    return b + a
