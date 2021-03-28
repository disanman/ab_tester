from logzero import logger
from json import dumps
from absizer import ABSizer

class ABTester():
    '''
    AB Tester is a set of utilities written on Python for evaluating AB Tests.
    You can initialize the code like:

    from abtester import ABTester
    ab_tester = ABTester()
    '''
    def __init__(self, A, B=None, significance=0.05, power=0.8, two_sided=True):
        ''' Initializes the AB Tester object
        Args:
            - A:                  (dict)  dictionary with two key-values: "conversions" and "impressions" (both have int values)
            - B:                  (dict or None)  dictionary with two key-values: "conversions" and "impressions" (both have int values)
            - significance level: (float) alpha, default: 0.05 (5%)
            - power:              (float) 1-beta, default: 0.8 (80%)
            - two_sided:          (bool)  wheter a two-sided test is used or not, default True (two-sided)
        '''
        logger.debug(f'Initializing ABTester with variant A: {A}, variant {B}, significance: {significance}, power: {power} and two-sided: {two_sided}]')
        self.A = A
        self.B = B
        self.significance = significance
        self.power = power
        self.two_sided = two_sided
        self.A['p_hat'] = self.A['conversions'] / self.A['impressions']
        logger.info(f'Base proportion (p_hat) of variant A (control): {self.A["p_hat"]:.2%}')
        self.sizer = ABSizer(self.A['p_hat'], significance, power, two_sided)
        if B:
            self.B['p_hat'] = self.B['conversions'] / self.B['impressions']
            # TODO: self.AB_stats = self._get_AB_test_stats()    # it will be a namedtuple for easier access with . notation

    def get_sample_size(self, method='approx1', p_hat=None, min_detectable_effect=0.1):
        ''' Calls the calculation of the required sample size by using on of the available methods:
         Args:
            - method:       (string) Options: 'approx1', 'evan_miller', 'R', 'standford'
            - p_hat:        (float or null) proportion, if None, the control variant A in initialization will be used
            - min_detectable_effect:   (float) minimum detectable effect, relative to base conversion rate.
        Returns:
            - sample size   (float)
        '''
        self.sizer.get_sample_size_using_method(method, p_hat, min_detectable_effect)

    def find_power(self):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError
