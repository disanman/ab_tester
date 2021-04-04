import pandas as pd
import numpy as np
# from statsmodels.distributions.empirical_distribution import ECDF
# Libraries used for plotting
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Ellipse
from matplotlib import rc                                                 # used to set matplotlib configuration parameters
rc('figure', facecolor='white', titlesize=20, dpi=80, figsize=(12, 8))    # background color (so it's visible in IPython), subtitle size, dots_per_inch (the higher the slower), default figsize
rc('grid', linestyle=':', color='gray', linewidth=0.3)
rc('font', size=12)                                                       # font_scale
rc('axes', edgecolor='lightgray', grid=True, labelsize=16)                # frame_color, enable grid per default, label_font_size
rc('lines', linewidth=2)                                                  # Line width, when plotting line plots
rc('savefig', dpi=200, format='svg')                                      # background color (so it's visible in IPython), subtitle size, dots_per_inch (the higher the slower), default figsize


class ABPlotter():
    ''' Plots results related with ABTests '''
    def plot_sample_size_vs_diff(self, min_effects, sample_sizes, significance, power, p_hat, desired=None):
        ''' Plots the sample size needed vs. minimum detectable difference in the input range given:
        Args:
            - sample_sizes: (array of floats) represents the sample sizes required for each minimum_detectable_change
            - min_effects:  (array of floats) array of min detectable change
            - significance: (float) significance level used in the test
            - power:        (float) power level used in the test
            - p_hat:        (float) initial proportion (base measurement in the control group)
            - desired:      (dict or None) a dict(desired_effect=float, sample_size=float) → values to be added in the chart
        '''
        plot = sns.lineplot(x=min_effects, y=sample_sizes, color='cornflowerblue', linewidth=4)
        plt.suptitle('Sample size required vs. minimum detectable difference')  # actual title
        plot.set(xlabel=f'Minimum detectable difference (% of base metric: {p_hat:.2%})', ylabel='Sample size',
                 title=fr'Significance level: {significance:.0%} ($\alpha$), power: {power:.0%} (1-$\beta$)')
        plot.set_xticklabels(f'{x:.0%}' for x in plot.get_xticks())
        # Set ylabel in thousands or millions
        plot.set_yticklabels(f'{x/1e6:,.1f}M' if x >= 1e6 else f'{x/1000:,.0f}k' for x in plot.get_yticks())
        if desired:
            # Add horizontal and vertical lines
            x = desired['desired_effect']
            y = desired['sample_size']
            plt.axvline(x, color='gray', linestyle=':')
            plt.axhline(y, color='gray', linestyle=':')
            # Add small ellipse and text
            ellipse = Ellipse(xy=(x, y), width=x*0.01, height=y*0.05, angle=0, color='gray', fill=False, linewidth=2, linestyle='-')
            plot.add_artist(ellipse)
            plt.text(x=x, y=y*1.05, s=f'↙ n ={y:.0f} @ {x:.2%}', size=14, color='gray')
        plt.show()

    def plot_sample_size_vs_diff_vs_significance(self, df, power, p_hat):
        ''' Plots various lines corresponding the sample size needed vs. minimum_detectable_change per different levels of significance level
        Args:
            - df:               (dataframe) with the columns: min_effects, significance and sample_size
            - power:            (float) power level used in the test
            - p_hat:            (float) base proportion
        '''
        colors = ('cornflowerblue', 'orange', 'green', 'salmon', 'olive', 'goldenrod')
        plt.figure()
        plot = sns.lineplot(x='min_effects', y='sample_size', hue='significance', data=df, linewidth=2, palette=colors)
        plt.suptitle('Sample size required vs. minimum detectable difference')  # actual title
        sig_levels = list(df.significance.value_counts().index)
        plot.set(xlabel=f'Minimum detectable difference (% of base metric: {p_hat:.2%})', ylabel='Sample size',
                 title=fr'Power: {power:.0%} (1-$\beta$)')
        plot.set_xticklabels(f'{x:.0%}' for x in plot.get_xticks())
        # Set ylabel in thousands or millions
        plot.set_yticklabels(f'{x/1e6:,.1f}M' if x >= 1e6 else f'{x/1000:,.0f}k' for x in plot.get_yticks())
        plt.show()

    def plot_power_vs_sample_size_vs_min_differences(self, df, p_hat, significance):
        ''' Plots the power of the AB Test vs. sample size in the input range:
        Args:
            - df:               (data frame) with sample_sizes, min_diff and power columns
            - p_hat:            (float) base proportion
            - significance:     (float) significance used
        '''
        colors = ('cornflowerblue', 'orange', 'green', 'salmon', 'olive', 'goldenrod')
        plt.figure()
        plot = sns.lineplot(x='sample_sizes', y='power', hue='min_diff', data=df, linewidth=2, palette=colors)
        plt.suptitle('Statistical power vs. sample size and minimum detectable difference')  # actual title
        plot.set(xlabel=f'Sample size', ylabel=fr'Power (1 - $\beta$)',
                title=fr'Significance level: {significance:0.0%} ($\alpha$)')
        plot.set_yticklabels(f'{x:.0%}' for x in plot.get_yticks())
        # Add horizontal line at the given 80% level
        plt.axhline(0.8, color='black', linestyle='dotted')
        # Set xlabel in thousands or millions
        plot.set_xticklabels(f'{x/1e6:,.1f}M' if x >= 1e6 else f'{x/1000:,.0f}k' for x in plot.get_xticks())
        # Reverse the order in the legend values:
        handles, labels = plot.get_legend_handles_labels()
        plot.legend(reversed(handles), reversed(labels), title=f'Min detectable difference \n (% of base metric: {p_hat:0.1%}):')
        plt.show()

