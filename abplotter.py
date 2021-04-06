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

    def plot_confidence_intervals(self, data, significance, two_sided):
        ''' Creates a point plot of the confidence intervals around the proportion
        estimation (p_hat) of the variants A and B in an AB Test
        Args:
            - data:         (data frame) with the A/B variant data
            - significance: (float) the significance (probability) level used to calculate the confidence intervals
            - two_sided:    (bool) indicates whether it has been two_sided or not
        '''
        mask_a = data['variant'] == 'A'
        # Is the central value p_hat for A variant smaller than B variant?
        a_lower_than_b = (data.loc[mask_a, 'p_hat'].iloc[0]) < (data.loc[~mask_a, 'p_hat'].iloc[0])
        # If A is lower than B, is there a significative difference? → is the right CI of A variant < than the left CI of B?
        if a_lower_than_b:
            right_ci_A = data.loc[mask_a, 'ci_right'].iloc[0]
            left_ci_B = data.loc[~mask_a, 'ci_left'].iloc[0]
            significative_diff = right_ci_A < left_ci_B
            fill_between = (right_ci_A, left_ci_B)
        else: # A is higher than B → is the right CI of B variant < than the left CI of A?
            right_ci_B = data.loc[~mask_a, 'ci_right'].iloc[0]
            left_ci_A = data.loc[mask_a, 'ci_left'].iloc[0]
            significative_diff = right_ci_B < left_ci_A
            fill_between = (right_ci_B, left_ci_A)
        df = data[['variant', 'p_hat', 'ci_left', 'ci_right']].melt(id_vars=['variant'], var_name='col', value_name='val')
        # Create point plot
        plt.figure()
        plot = sns.pointplot(y='variant', x='val', data=df, linewidth=2, hue='variant', capsize=0.1)
        # Set titles and labels
        plt.suptitle('Comparison of the confidence intervals of the two variants A and B', fontsize=18, y=0.96)
        if significative_diff:
            title = f'There is significative difference between the confidence intervals (they do not overlap)'
        else:
            title = f'The two confidence intervals overlap, there might not be a significative difference'
        title += fr' ($\alpha$:{significance:0.1%} ' + ('Two-sided' if two_sided else 'One-sided') + ')'
        plot.set(xlabel='Base metric', ylabel='Variant', title=title)
        # Set x-labels in percentages
        plot.set_xticklabels(f'{x:.1%}' for x in plot.get_xticks())
        # Add fill color, according to the case
        fill_color = 'green' if significative_diff else 'red'
        x = np.linspace(fill_between[0], fill_between[1], 10)
        plot.fill_between(x, y1=0, y2=1, where=(x < 1), facecolor=fill_color, alpha=0.3)
        return plot

    def plot_ab_variants(self, data):
        ''' Creates a stacked bar chart with the representation of the two variants A/B and the proportion of each one
        Args:
            - data:         (data frame) with the A/B variant data
        '''
        df = data[['variant', 'conversions', 'impressions']].copy()
        df['impressions'] = df['impressions'] - df['conversions']   # conversions are part of the impressions!
        df = df.melt(id_vars='variant', var_name='col', value_name='value')
        plot = self.create_stacked_bar_plot(x='variant', y='value', break_by_col='col', data=df, colors=('cornflowerblue', 'goldenrod'))
        # Rotate axis:
        for tick in plot.get_xticklabels():
            tick.set_rotation(0)
        plt.suptitle('A/B variants', fontsize=18, y=0.96)
        mask_a = data['variant'] == 'A'
        title = f'Conversion rate in variant A: {data.loc[mask_a, "p_hat"].iloc[0]:0.2%}, in variant B: {data.loc[~mask_a, "p_hat"].iloc[0]:0.2%}'
        plot.set(xlabel='Variant', ylabel='Sample size per variant', title=title)
        plot.set_yticklabels(f'{x/1e6:,.1f}M' if x >= 1e6 else f'{x/1000:,.0f}k' for x in plot.get_yticks())
        return plot

    @staticmethod
    def create_stacked_bar_plot(x, y, break_by_col, data, categories=None, colors=('cornflowerblue', 'orange', 'goldenrod', 'green', 'olive'), figsize=(15,7)):
        '''Creates a stacked bar plot, uses the bar plot option in pandas dataframe, but first it pivots the data
        Args:
            - x:            the column used to plot x
            - y:            the column used to plot y
            - categories:    if given, the data will be sorted as indicated in those categories
            TODO: improve documentation
        '''
        df = data.copy()
        if not categories:
            categories = df[break_by_col].unique()
        # Convert column to categorical → so the order can be implemented
        df[break_by_col] = pd.Categorical(data[break_by_col], categories=categories, ordered=True)
        # Pivot data!
        df = df.reset_index().pivot(index=x, columns=break_by_col, values=y)    # Todo: is it needed the aggregation function?
        # Make the plot!
        ax = df.plot.bar(stacked=True, figsize=figsize, color=colors)
        # Fix order in the legend! → reverse it
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(reversed(handles), reversed(labels))
        return ax
