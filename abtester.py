import numpy as np
import pandas as pd
import logging
from logzero import logger
from json import dumps
from absizer import ABSizer
from abplotter import ABPlotter
from scipy.stats import norm

logger.setLevel(logging.INFO)    # may choose DEBUG

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
            self.AB_stats = self._get_ab_test_stats()    # it will be a dataframe

    def get_sample_size(self, method='approx1', p_hat=None, min_detectable_effect=0.1, significance=None):
        ''' Calls the calculation of the required sample size by using on of the available methods:
         Args:
            - method:                  (string) Options: 'approx1', 'evan_miller', 'R', 'standford'
            - p_hat:                   (float or null) proportion, if None, the control variant A in initialization will be used
            - min_detectable_effect:   (float) minimum detectable effect, relative to base conversion rate, defaults to 0.1 (10%)
            - significance: (float or null) alpha, in case of null, defaults to the significance level given in the initialization
        Returns:
            - sample size              (float)
        '''
        sample_size = self.sizer.get_sample_size_using_method(method, p_hat, min_detectable_effect, significance)
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


    def plot_sample_size_vs_diff_vs_significance(self, diff_range=(0.05, 0.15), steps=50, sig_levels=(0.05, 0.03, 0.01), p_hat=None, method='approx1'):
        ''' Gets the data (and plots) the required sample size for the given power, minimum detectable difference and significance levels.
        Args:
            - diff_range:           (tuple of floats) Tuple that represents the interval for which to construct the
                                      plot: (min_detectable_effect, max_detectable_effect), defaults to (0.05, 0.15) = (5%, 15%)
            - steps:                (int) number of datapoints to be plotted in the given interval per line, defults to 50
            - sig_levels:           (tuple of floats) the various levels of significance level to be used when plotting
            - p_hat:                (float or null) base proportion, if None, the control variant A in initialization will be used
            - method:               (string) Options: 'approx1', 'evan_miller', 'R', 'standford'
        '''
        if not p_hat:
            p_hat = self.A['p_hat']
        step_size = (diff_range[1] - diff_range[0]) / steps
        min_effects = np.arange(start=diff_range[0], stop=diff_range[1], step=step_size)   # range definition
        # Create data frame of sample sizes required per significance level and min_detectable_effect:
        data = dict()
        for significance in sig_levels:
            data[significance] = [self.get_sample_size(method=method, p_hat=p_hat, min_detectable_effect=min_effect, significance=significance) for min_effect in min_effects]
        df = pd.DataFrame.from_dict(data)
        df['min_effects'] = min_effects
        df = df.melt(id_vars=['min_effects'], var_name='significance', value_name='sample_size')        # id_vars: those columns that will remain, the others will be melted into rows
        df['significance'] = pd.Categorical(f'{val:.0%}' for val in df['significance'])    # make it categorical-string and in %
        plot = self.plotter.plot_sample_size_vs_diff_vs_significance(df, power=self.power, p_hat=p_hat)

    def plot_power_vs_sample_size_vs_min_differences(self, sample_size_range=(500, 1000), steps=50, min_diffs=(0.05, 0.1, 0.15), p_hat=None, significance=None):
        ''' Plots the power of the AB Test vs. sample size in the input range:
        Args:
            - min_sample_size: (int) minimum sample size in plot (x-axis)
            - max_sample_size: (int) maximum sample size in plot (x-axis)
            - step_sample_size: (int) '''
        p_hat = self.A['p_hat'] if not p_hat else p_hat
        significance = self.significance if not significance else significance
        step_size = (sample_size_range[1] - sample_size_range[0]) / steps
        sample_sizes = np.arange(start=sample_size_range[0], stop=sample_size_range[1], step=step_size)
        # Create data frame with data:
        data = dict()
        for min_diff in min_diffs:
            data[min_diff] = [self.sizer.find_power_given_min_effect_and_sample_size(min_detectable_effect=min_diff, sample_size=sample_size, p_hat=p_hat, significance=significance) for sample_size in sample_sizes]
        df = pd.DataFrame.from_dict(data)
        df['sample_sizes'] = sample_sizes
        df = df.melt(id_vars=['sample_sizes'], var_name='min_diff', value_name='power')        # id_vars: those columns that will remain, the others will be melted into rows
        df['min_diff'] = pd.Categorical([f'{val:.0%}' for val in df['min_diff']], categories=[f'{val:.0%}' for val in min_diffs], ordered=True)    # make it categorical-string and in %
        plot = self.plotter.plot_power_vs_sample_size_vs_min_differences(df, p_hat, significance)

    def _get_z_val(self, prob=None, two_sided=None):
        ''' Returns the z value of a normal distribution for a given significance level (probability value) '''
        # Find the z value accordingly with one_sided or two_sided test:
        if not two_sided:
            two_sided = self.two_sided
        if not prob:
            prob = (self.significance / 2) if two_sided else (self.significance)   # alpha/2 if two-sided
        z = -norm.ppf(prob)   # finds the z-value for the given probability
        return z

    def _get_variant_confidence_interval(self, variant, significance=None, two_sided=None):
        ''' Finds the confidence interval around the central proportion value (p_hat) given the
        Args:
            - variant:          (dict)  dictionary with min two key-values: "conversions" and "impressions" (both have int values)
            - significance:     (float or None) alpha, if not given, the one used at initialization will be used
            - two_sided:        (bool)  wheter a two-sided test is used or not, defaults to value given at initialization
        Uses the z-value given the input significance and two_sided test configuration (uses the initialization values or the ones in input)
        '''
        if not significance:
            significance = self.significance
        if not two_sided:
            two_sided = self.two_sided
        impressions, p_hat = variant['impressions'], variant['p_hat']
        if impressions * p_hat < 5:
            logger.warning(f'Warning: the normal approximation does not hold for variant: {variant}')
        # Calculating the standard_error of the sample (assuming the distribution is like a binomial): p_hat · (1 - p_hat) ≝ sample variance (S²)
        standard_error = np.sqrt(p_hat * (1 - p_hat) / impressions)
        z = self._get_z_val(significance, two_sided)
        margin_of_error = z * standard_error   # assumes it is normally distributed
        left = p_hat - margin_of_error
        right = p_hat + margin_of_error
        logger.info(f'p_hat: {p_hat:.2f}, z: {z:.2f}, margin of error: {margin_of_error:.3f}')
        logger.info(f'Confidence interval: ({left:.3f}, {right:.3f})')
        confidence_interval = (left, right)
        return confidence_interval

    def _get_ab_test_stats(self):
        # Create data frame with variant data
        A = self.A
        A['variant'] = 'A'
        A['ci_left'], A['ci_right'] = self._get_variant_confidence_interval(A)
        B = self.B
        B['variant'] = 'B'
        B['ci_left'], B['ci_right'] = self._get_variant_confidence_interval(B)
        data = pd.DataFrame([A, B])
        return data

    def plot_confidence_intervals(self):
        plot = self.plotter.plot_confidence_intervals(self.AB_stats, self.significance, self.two_sided)
        return plot

    def plot_ab_variants(self):
        '''
        Plots the two variants of the test as a stacked bar chart with two colors
        '''
        if not self.B:
            raise ValueError('Missing information related to variant B, please input it when initialising the ABTester object.')
        data = self.AB_stats
        plot = self.plotter.plot_ab_variants(data)
        return plot
