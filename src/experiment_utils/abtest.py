"""Utilities for A/B test."""

from collections import namedtuple

import numpy as np
from scipy.stats import norm, t


class ABTest():
    """Class for A/B test."""
    
    def __init__(self, alpha=0.05, type="two-tailed"):
        """Initiate the class.

        Args:
            alpha (float): significance level for the test.
            type (str): whether the test is two-sided, left-sided or right-sided.

        Returns:
            None.
        """
        self._alpha = alpha

        if not isinstance(type, str):
            raise TypeError("Test `type` provided is not valid.")
        if "two" in type.lower():
            self._type = "two-tailed"
        elif "left" in type.lower():
            self._type = "left-tailed"
        elif "right" in type.lower():
            self._type = "right-tailed"
        else:
            raise ValueError("Test `type` provided is not a valid option.")

    def _get_pooled_prob(self, X_exp, X_ctrl, N_exp, N_ctrl):
        """Calculate pooled probability.
        
        Args:
            X_exp (int): Number of positive in treatment group.
            X_ctrl (int): Number of positive in control group.
            N_exp (int): Total number of samples in treatment group.
            N_ctrl (int): Total number of samples in control group.

        Returns:
            pooled_p (float): pooled probabilty estimated from two samples.
        """
        pooled_p = (X_exp + X_ctrl) / (N_exp + N_ctrl)
        return pooled_p

    def _get_pooled_se(self, pooled_p, N_exp, N_ctrl):
        """Calculate pooled standard error.

        Args:
            pooled_p (float): pooled probability.
            N_exp (int): Total number of samples in treatment group.
            N_ctrl (int): Total number of samples in control group.

        Returns:
            pooled_se (float): pooled standard error.
        """
        pooled_se = np.sqrt(pooled_p * (1 - pooled_p) * (1/N_exp + 1/N_ctrl))
        return pooled_se

    def _get_z_confidence_interval(self, point_estimate, standard_error):
        """Calculate confidence interval for a given point estimate and standard error.

        Args:
            point_estimate (float): point estimate of a certain metric.
            standard_error (float): estimated standard error.

        Returns:
            confidence_interval (namedtuple): lower and upper bound of confidence interval.
        """
        if self._type == "two-tailed":
            z_abs = norm.ppf(1 - self._alpha/2)
            lower = point_estimate - z_abs * standard_error
            upper = point_estimate + z_abs * standard_error
        elif self._type == "right-tailed": # test if increase
            z_abs = norm.ppf(1 - self._alpha)
            lower = -np.inf
            upper = point_estimate + z_abs * standard_error
        elif self._type == "left-tailed": # test if decrease
            z_abs = norm.ppf(1 - self._alpha)
            lower = point_estimate - z_abs * standard_error
            upper = np.inf

        range_tuple = namedtuple('range_tuple', 'lower upper')
        confidence_interval = range_tuple(lower, upper)
        return confidence_interval

    def _get_t_confidence_interval(self, point_estimate, standard_error, degree_of_freedom):
        """Calculate confidence interval for a given point estimate and standard error.

        Args:
            point_estimate (float): point estimate of a certain metric.
            standard_error (float): estimated standard error.
            degree_of_freedom (float): degree of freedom.

        Returns:
            confidence_interval (namedtuple): lower and upper bound of confidence interval.
        """
        if self._type == "two-tailed":
            t_abs = t.ppf(1 - self._alpha/2, degree_of_freedom)
            lower = point_estimate - t_abs * standard_error
            upper = point_estimate + t_abs * standard_error
        elif self._type == "right-tailed": # test if increase
            t_abs = norm.ppf(1 - self._alpha, degree_of_freedom)
            lower = -np.inf
            upper = point_estimate + t_abs * standard_error
        elif self._type == "left-tailed": # test if decrease
            t_abs = norm.ppf(1 - self._alpha, degree_of_freedom)
            lower = point_estimate - t_abs * standard_error
            upper = np.inf

        range_tuple = namedtuple('range_tuple', 'lower upper')
        confidence_interval = range_tuple(lower, upper)
        return confidence_interval

    def _get_significance(self, confidence_interval, benchmark):
        """Check whether the outcome is statistically signficant.
        
        Args:
            confidence_interval (namedtuple): confidence interval with upper and lower bound.
            benchmark (float): benchmark to determine significance.
        
        Returns:
            significant (bool): Whether the outcome is significant.
        """
        if self._type == "two-tailed":
            if confidence_interval.lower > benchmark or confidence_interval.upper < benchmark:
                significant = True
            else:
                significant = False
        elif self._type == "right-tailed":
            if confidence_interval.lower > benchmark:
                significant = True
            else:
                significant = False
        elif self._type == "left-tailed":
            if confidence_interval.upper < benchmark:
                significant = True
            else:
                significant = False

        return significant
        
    def test_prob(self, X_exp, X_ctrl, N_exp, N_ctrl, practical_diff=0.0, verbose=0):
        """Perform A/B test on probability.
        
        Args:
            X_exp (int): Number of positive in treatment group.
            X_ctrl (int): Number of positive in control group.
            N_exp (int): Total number of samples in treatment group.
            N_ctrl (int): Total number of samples in control group.
            practical_diff (float): Difference required to reach practical significance of the test.
            verbose (int): Whether to print metrics and test stats.

        Returns:
            stat_significant (bool): Whether the difference is statistically significant.
            practical_significant (bool): Whether the difference is practically significant.
        """
        inputs = [X_exp, X_ctrl, N_exp, N_ctrl]

        # check for negative or non-integer values
        if any(i < 0 for i in inputs) or not all(int(i) == i for i in inputs):
            raise ValueError("All inputs should be nonnegative integers.")
        
        # check for valid probability
        if X_exp > N_exp or X_ctrl > N_ctrl:
            raise ValueError("Positive samples should not be greater than total samples.")

        p_exp, p_ctrl = X_exp / N_exp, X_ctrl / N_ctrl
        d_obs = p_exp - p_ctrl

        pooled_p = self._get_pooled_prob(X_exp, X_ctrl, N_exp, N_ctrl)
        pooled_se = self._get_pooled_se(pooled_p=pooled_p, N_exp=N_exp, N_ctrl=N_ctrl)

        d_interval = self._get_z_confidence_interval(point_estimate=d_obs, 
                                                   standard_error=pooled_se)
        
        stat_significant = self._get_significance(d_interval, 0.0)
        practical_signficant = self._get_significance(d_interval, practical_diff)

        if verbose > 0:
            print(f'Sample size in treatment group: {int(N_exp)}')
            print(f'Observed probability in treatment group: {p_exp:.2%}\n')
            print(f'Sample size in control group: {int(N_ctrl)}')
            print(f'Observed probability in control group: {p_ctrl:.2%}\n')
            print(f'Observed difference in probability (treatment - control): {d_obs:.2%}')
            print(f'Confidence interval for probability diff: ({d_interval.lower:.2%}, {d_interval.upper:.2%})\n')

        print(f'Is the test statistically significant? {stat_significant}')
        print(f'Is the test practically signficant ({practical_diff:.2%})? {practical_signficant}')      
 
        return stat_significant, practical_signficant

    def test_mean(self, arr_exp, arr_ctrl, practical_diff=0.0, verbose=0):
        """Perform A/B test on difference of two sample means.
        
        Args:
            arr_exp (array-like): Values of sample 1.
            arr_ctrl (array-like): Values of sample 2.
            practical_diff (float): Difference required to reach practical significance of the test.
            verbose (int): Whether to print metrics and test stats.

        Returns:
            stat_significant (bool): Whether the difference is statistically significant.
            practical_significant (bool): Whether the difference is practically significant.
        """
        mu_exp, mu_ctrl = np.mean(arr_exp), np.mean(arr_ctrl)
        N_exp, N_ctrl = len(arr_exp), len(arr_ctrl)
        sd_exp, sd_ctrl = np.std(arr_exp), np.std(arr_ctrl)

        d_obs = mu_exp - mu_ctrl
        pooled_sd = np.sqrt( ((N_exp - 1) * sd_exp**2 + (N_ctrl - 1) * sd_ctrl**2) / (N_exp + N_ctrl - 2 ) )
        pooled_se = pooled_sd * np.sqrt(1/N_exp + 1/N_ctrl)

        d_interval = self._get_t_confidence_interval(point_estimate=d_obs, 
                                                    standard_error=pooled_se, 
                                                    degree_of_freedom=N_exp + N_ctrl - 2)

        stat_significant = self._get_significance(d_interval, 0.0)
        practical_signficant = self._get_significance(d_interval, practical_diff)

        if verbose > 0:
            print(f'Sample size in treatment group: {int(N_exp)}')
            print(f'Observed mean in treatment group: {mu_exp:.4}\n')
            print(f'Sample size in control group: {int(N_ctrl)}')
            print(f'Observed mean in control group: {mu_ctrl:.4}\n')
            print(f'Observed difference in mean (treatment - control): {d_obs:.4}')
            print(f'Confidence interval for mean diff: ({d_interval.lower:.4}, {d_interval.upper:.4})\n')

        print(f'Is the test statistically significant? {stat_significant}')
        print(f'Is the test practically signficant ({practical_diff:.4})? {practical_signficant}')      
 
        return stat_significant, practical_signficant

        