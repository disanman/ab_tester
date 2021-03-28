
class ABTester():
    '''
    AB Tester is a set of utilities written on Python for evaluating AB Tests.
    You can initialize the code like:

    from abtester import ABTester
    ab_tester = ABTester()
    '''
    def __init__(self):
        pass

    def find_sample_size(self, method='approx1'):
        raise NotImplementedError

    def find_power(self):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError
