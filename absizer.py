import numpy as np
import statsmodels.stats.api as sms
from logzero import logger
from scipy.stats import norm, binom
from math import sqrt

class ABSizer():
    ''' Finds the size needed to perform an AB Test by using different methodologies '''
    def __init__(self, p_hat, significance=0.05, power=0.8, two_sided=True):
        ''' Initializes the AB Sizer object
        Args:
            - p_hat:              (float) the proportion in the variant A (control)
            - significance level: (float) alpha, default: 0.05 (5%)
            - power:              (float) 1-beta, default: 0.8 (80%)
            - two_sided:          (bool)  wheter a two-sided test is used or not, default True (two-sided)
        '''
        logger.debug(f'Initializing ABSizer with p_hat: {p_hat}, significance: {significance}, power: {power} and two-sided: {two_sided}]')
        self.p_hat = p_hat
        self.significance = significance
        self.power = power
        self.two_sided = two_sided

    def get_sample_size_using_method(self, method='approx1', p_hat=None, min_detectable_effect=0.1):
        ''' Calculation the required sample size by using on of the available methods:
         Args:
            - method:       (string) Options: 'approx1', 'evan_miller', 'R', 'standford'
            - p_hat:        (float or null) proportion, if None, the control variant A in initialization will be used
            - min_detectable_effect:   (float) minimum detectable effect, relative to base conversion rate.
        Returns:
            - sample size   (float)
        '''
        if not p_hat:
            p_hat = self.p_hat
        if method == 'approx1':
            self.get_sample_size_approx_1(p_hat, min_detectable_effect)
        elif method == 'evan_miller':
            self.get_sample_size_evan_miller(p_hat, min_detectable_effect)
        elif method == 'R':
            self.get_sample_size_as_R(p_hat, min_detectable_effect)
        elif method == 'standford':
            self.get_sample_size_standford(p_hat, min_detectable_effect)
        else:
            raise ValueError(f'error in method input: {method}')

    def get_sample_size_approx_1(self, p_hat=None, min_detectable_effect=0.05):
        '''
        Finds the sample size using the formula: n=16·σ²/Δ², where:
          - σ is the standard deviation of the performance measure, σ² would be the variance
          - Δ is the sensitvity or the amount of change you want to detect (min detectable diff between control and treatment).
        Example, in an e-commerce:
            - p_hat: 2% users who visit end up purchasing
            - What is the minimum sample size needed for detecting a 5% `change in conversion rate`?
            - A purchase, a convention event, can be modeled as a Bernoulli trial with p = 0.05
            - For a Bernoulli distribution, σ = √[p·(1-p)]
                - n = 16·σ²/Δ² = 16·(0.02·(1-0.02)) / (0.02·0.05)² = 121600 users per variant
        '''
        if not p_hat:
             p_hat = self.p_hat
        logger.debug('Finding sample size, method: approx1...')
        variance = p_hat * (1 - p_hat)
        Delta = p_hat * min_detectable_effect
        n = 16 * variance / Delta**2
        logger.debug(f'variance, σ²: {variance:.4f}, σ: {sqrt(variance)}, Δ: {Delta:.4f}')
        logger.info(f'\nA minimum sample size of \
                     \n  n = {n:.0f} is needed\n\
                     \n  to detect a change of {min_detectable_effect:.0%} (relative) of a base proportion of {p_hat:.2%}')
        return n

    def get_sample_size_evan_miller(self, p_hat=None, min_detectable_effect=0.05):
         '''
         Based on https://www.evanmiller.org/ab-testing/sample-size.html
         Explanation here: http://www.alfredo.motta.name/ab-testing-from-scratch/
         and here, two sided or one sided: https://www.itl.nist.gov/div898/handbook/prc/section2/prc242.htm
         Args:
             - p_hat:                   (float) the estimation of proportion
             - min_detectable_effect:   (float) minimum detectable effect, relative to base conversion rate.
         - TODO: add option to select whether the min_detectable_effect is absolute or relative
         '''
         if not p_hat:
             p_hat = self.p_hat
         delta = p_hat * min_detectable_effect
         if self.two_sided:
             t_alpha = norm.ppf(1.0 - self.significance / 2)  # two-sided interval
         else:
             t_alpha = norm.ppf(1.0 - self.significance)  # one-sided interval
         t_beta = norm.ppf(self.power)
         sd1 = np.sqrt(2 * p_hat * (1.0 - p_hat))
         sd2 = np.sqrt(p_hat * (1.0 - p_hat) + (p_hat + delta) * (1.0 - p_hat - delta))
         sample_size = ((t_alpha * sd1 + t_beta * sd2) / delta) ** 2
         logger.info(f'\nA minimum sample size of \
                      \n  n = {sample_size:.0f} is needed\n\
                      \n  to detect a change of {min_detectable_effect:.0%} (relative) of a base proportion of {p_hat:.2%}\
                      \n  with a power of {self.power:.0%}\
                      \n  and a significance level of {self.significance:.1%}')
         return sample_size

    def get_sample_size_as_R(self, p_hat=None, min_detectable_effect=0.05):
        '''
        Sample size needed for a two-sided test, given a minimun dettectable effect
        Args:
            - p_hat:                  (float) the base proportion
            - min_detectable_effect:  (float) Minimum detectable effect, relative to base conversion rate.
        Matches the results obtained in R by using:
        # power.prop.test(p1=.1, p2=.12, power=0.8, alternative='two.sided', sig.level=0.05, strict=T)
        '''
        if not p_hat:
            p_hat = self.p_hat
        effect_size = sms.proportion_effectsize(p_hat, p_hat * (1 + min_detectable_effect))
        sample_size = sms.NormalIndPower().solve_power(effect_size, power=self.power, alpha=self.significance, ratio=1)
        # alternative way of calculating it:
        # smp.zt_ind_solve_power(nobs1=None, effect_size=es, alpha=0.05, power=0.8, ratio=1, alternative='two-sided')
        logger.info(f'\n A minimum sample size of \
                     \n  n = {sample_size:.0f} is needed\n\
                     \n  to detect a change of {min_detectable_effect:.0%} (relative) of a base proportion of {p_hat:.2%}\
                     \n  with a power of {self.power:.0%}\
                     \n  and a significance level of {self.significance:.1%}')
        return sample_size

    def get_sample_size_standford(self, p_hat=None, min_detectable_effect=0.05):
        """Returns the minimum sample size to set up a split test
        Arguments:
           - p_hat:                  (float) the base proportion
           - mde (float): minimum change in measurement between control
           - group and test group if alternative hypothesis is true, sometimes referred to as minimum detectable effect
        Returns:
            minimum sample size (float)
        References:
            Stanford lecture on sample sizes
            http://statweb.stanford.edu/~susan/courses/s141/hopower.pdf
        """
        # TODO: fix this one!!!!
        if not p_hat:
           p_hat = self.p_hat
        # average of probabilities from both groups, pooled_probability:
        pooled_prob = (p_hat + p_hat * (1 + min_detectable_effect)) / 2
        sigma = sqrt(pooled_prob * (1 - pooled_prob))
        # Delta: the effect size:the number of standard deviations the true mean is away from the test done
        Delta = (p_hat - p_hat*(1 + min_detectable_effect)) / sigma
        # alternative way: effect_size = sms.proportion_effectsize(p_hat, p_hat * (1 + min_detectable_effect))
        # standard normal distribution used to determine z-values
        standard_norm = norm(0, 1)

        # find Z_beta from desired power
        Z_beta = standard_norm.ppf(self.power)

        # find Z_alpha
        if self.two_sided:
            Z_alpha = standard_norm.ppf(1 - self.significance / 2)
        else:
            Z_alpha = standard_norm.ppf(1 - self.significance)

        sample_size = ((Z_beta + Z_alpha)**2 / Delta**2)
        logger.info(f'\n A minimum sample size of \
                     \n  n = {sample_size:.0f} is needed\n\
                     \n  to detect a change of {min_detectable_effect:.0%} (relative) of a base proportion of {p_hat:.2%}\
                     \n  with a power of {self.power:.0%}\
                     \n  and a significance level of {self.significance:.1%}')
        return sample_size


