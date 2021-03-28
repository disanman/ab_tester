import numpy as np
from logzero import logger
from json import dumps
from absizer import ABSizer
from abplotter import ABPlotter

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
        self.plotter = ABPlotter()
        if B:
            self.B['p_hat'] = self.B['conversions'] / self.B['impressions']
            # TODO: self.AB_stats = self._get_AB_test_stats()    # it will be a namedtuple for easier access with . notation

    def get_sample_size(self, method='approx1', p_hat=None, min_detectable_effect=0.1):
        ''' Calls the calculation of the required sample size by using on of the available methods:
         Args:
            - method:                  (string) Options: 'approx1', 'evan_miller', 'R', 'standford'
            - p_hat:                   (float or null) proportion, if None, the control variant A in initialization will be used
            - min_detectable_effect:   (float) minimum detectable effect, relative to base conversion rate, defaults to 0.1 (10%)
        Returns:
            - sample size              (float)
        '''
        sample_size = self.sizer.get_sample_size_using_method(method, p_hat, min_detectable_effect)
        return sample_size

    def find_power(self):
        raise NotImplementedError

    def plot_sample_size_vs_diff(self, diff_range=(0.05, 0.15), steps=50, p_hat=None, method='approx1', desired_effect=None):
        ''' Gets the data (and plots) the required sample size for the given power and statistical significance.
        Args:
            - diff_range:           (tuple of floats) Tuple that represents the interval for which to construct the
                                      plot: (min_detectable_effect, max_detectable_effect), defaults to (0.05, 0.15) = (5%, 15%)
            - steps:                (int) number of datapoints to be plotted in the given interval, defults to 50
            - p_hat:                (float or null) proportion, if None, the control variant A in initialization will be used
            - method:               (string) Options: 'approx1', 'evan_miller', 'R', 'standford'
            - desired_effect:        (float or null) if given, it will be added to the chart in the form of vertical lines
                                                    and the corresponding sample size will be also added
        '''
        step_size = (diff_range[1] - diff_range[0]) / steps
        min_effects = np.arange(start=diff_range[0], stop=diff_range[1], step=step_size)   # range definition
        sample_sizes = [self.get_sample_size(method=method, p_hat=p_hat, min_detectable_effect=min_effect) for min_effect in min_effects]
        if desired_effect and (diff_range[0] <= desired_effect <= diff_range[1]):   # if given and within range
            resulting_sample_size = self.get_sample_size(method=method, p_hat=p_hat, min_detectable_effect=desired_effect)
            desired = dict(desired_effect=desired_effect, sample_size=resulting_sample_size)
        else:
            desired = None
        self.plotter.plot_sample_size_vs_diff(min_effects, sample_sizes, significance=self.significance, power=self.power, p_hat=self.A['p_hat'], desired=desired)


