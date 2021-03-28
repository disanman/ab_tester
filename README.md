```
                            _    ____    _____         _
                           / \  | __ )  |_   _|__  ___| |_ ___ _ __
                          / _ \ |  _ \    | |/ _ \/ __| __/ _ \ '__|
                         / ___ \| |_) |   | |  __/\__ \ ||  __/ |
                        /_/   \_\____/    |_|\___||___/\__\___|_|
Some utilities for evaluating AB Tests
```
# What is an AB Test?
It's a user experience research methodology. It consists of a randomized experiment with two product variants: A and
B. The two variants are compared. From a business perspective, we would like to know if the performance of a certain
variant of a user's experience outperforms the other, thus helping the business achieve more effectively its goals
(i.e. increasing conversions, revenue, user engagement, etc). At the base of an AB test, [hypothesis testing](https://en.wikipedia.org/wiki/Statistical_hypothesis_testing) is used
(a statistical approach to inference).

# What is AB Tester (this package)? [WIP]
It's a set of utilities written on Python for evaluating AB Tests, like:
  - [ ] Sample size calculation by using different methodologies:
      - [ ] Approximate approach by using n=16·σ²/Δ²
      - [ ] Similar approach to the one used in R with the function....
      - [ ] Similar approach to the one used in the nice [Evan-Miller calculator](http://www.evanmiller.org/ab-testing/sample-size.html#!20;85;5;5;0)
  - [ ] Graphical tools:
      - [ ] to be defined...

# Why has been this created?
This is just some tests I have been doing with the available functions in Python, and some AB Tests courses I have done.
I just compare, test, create functionality and put it in git so maybe it can be useful to anyone doing some AB Tests.
There are many more packages like this, which are also much more complete than this one, each one allows to test
different things (I will 'borrow' parts of their code here):
  - [pyAB](https://github.com/AdiVarma27/pyAB): it has some really nice charts!
  - [abracadabra](https://github.com/quizlet/abracadabra): nice charts, both frequentist and Bayesian approach
  - [ABTests](https://github.com/leodema/ABtests): has some ABTest reports
  - [abito](https://github.com/avito-tech/abito): offers the possibility to make bootstrap analysis
  - Bayesian approach:
      - [AByes](https://github.com/cbellei/abyes): Bayesian
      - [Babtest](https://github.com/tcassou/babtest)

So why to bother creating a new package? well for me it's more like 'learn by doing', that way I learn by testing,
hacking, copying, checking how it works, experiment, fail and improve. I also like programming in Python so creating a
nice python interface to this relatively complex topic seems like a nice hobby to me.

# How to use the it? [WIP]
Just initialize an ABTester object by using something like:
```python
# Imports the class ABTester (you can find the code in the file abtester.py)
from abtester import ABTester

# Initialize object ab_tester
ab_tester = ABTester()

ab_tester.find_sample_size(method='approx1')
```

