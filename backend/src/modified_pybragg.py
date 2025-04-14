import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as sc

import numpy as np
import math
from scipy.optimize import curve_fit
from scipy.stats import norm, moyal, rv_continuous
import scipy.stats as stats
# needed for spline
from scipy.interpolate import interp1d
# parabolic cylinder function D
from scipy import special
from itertools import product
import scipy.odr as odr
from typing import Callable
from functools import partial


def fitBP(z, D, D_unc, method='bortfeld', rel_resolution=0.01):
    """ Automated fit and characterization of a pragg curve.
    
    Parameters
    -----------
    :param z: depth in phantom in cm
    :param D: dose at depth z
    :param method: "bortfeld" for full fit with Bortfeld approximation. "spline" for fast and simple spline fit (default "bortfeld")
    :param rel_resolution: fraction of z step width for the fit function characterization for range quantities like R80. (default 0.01)
  
    Returns
    --------
    :returns:  D(z) - depth dose in depth z
    """

    # check for validity of relevant input arguments
    assert len(z) == len(D), f"z and D need to have same length but are len(z)={len(z)} and len(D)={len(D)}"
    assert method in ['spline', 'bortfeld'], f"method can only be 'spline' or 'bortfeld' but is {method}"

    # define some accuracy settings
    resolution = rel_resolution*np.min(np.diff(z))

    # fit spline with given precision to curve
    spline_func = interp1d(z, D, kind='cubic')
    z_spline    = np.linspace(min(z), max(z), round((max(z)-min(z)) / resolution ))
    quantities  = characterize_z_D_curve(z_spline, spline_func(z_spline))

    # return interpolation for reference as well
    quantities['spline_func'] = spline_func

    # if spline fit only, return already
    if method == 'spline':
        return quantities

    # use precomputed values for further computations using bortfeld fit
    if method == 'bortfeld':
        # create init parameters from
        p         = 1.77 # result from paper Fig. 1
        alpha     = 0.0022 # result from paper Fig. 1
        R0        = quantities['R80D']
        E0        = (R0/alpha)**(1/p) # paper: Eq. (4)
        sigmaMono = (0.012*R0**0.935) # paper: Eq. (18)
        sigmaE0   = 0.01*E0 # assumtion that Delta E will be small
        sigma     = np.sqrt(sigmaMono**2+sigmaE0**2*alpha**2*p**2*E0**(2*p-2)) # paper: Eq. (19)

        # normalization constant for fit
        A = quantities['D100']
        # normalization constant for second part of equation, depends on the epsilon from the original publication
        k = 0.01394
        p, c = curve_fit(
            bortfeld, z, D,
            sigma=D_unc,
            absolute_sigma=True,
            p0 = [A, R0, sigma, p, k],
            bounds=( # limits
            #               D100        |    R0     |  sigma   |   p  |  k  | 
                 ( .5*quantities['D100'], R0-3*sigma, 0.5*sigma,   0.5,    0),
                 (1.5*quantities['D100'], R0+3*sigma, 3  *sigma,   2.5,  0.1),
             )
           )
        
        # return for easy access
        quantities['bortfeld_fit_results'] = {var: {'nominal': nom, 'std': std} for var, nom, std in zip(['D100', 'R0', 'sigma', 'p', 'k'], p, np.diag(c))}

        # return parameter vector and cov matrix as well
        quantities['bortfeld_fit_p']       = p
        quantities['bortfeld_fit_cov']     = c

        # recalc some quantities if needed
        bortfeld_quantities = characterize_z_D_curve(z_spline, bortfeld(z_spline, *p))
        # overwrite results from spline fit
        quantities.update(bortfeld_quantities)

        return quantities


# adapted from https://gray.mgh.harvard.edu/attachments/article/293/BraggCurve.py
def cyl_gauss(a,x):
    """Calculate product of Gaussian and parabolic cylinder function"""
    y = np.zeros_like(x)
    branch = -12.0   #for large negative values of the argument we run into numerical problems, need to approximate result

    x1 = x[x<branch]
    y1 = np.sqrt(2*np.pi)/special.gamma(-a)*(-x1)**(-a-1)
    y[x<branch] = y1

    x2 = x[x>=branch]
    y2a = special.pbdv(a,x2)[0]     #special function yielding parabolic cylinder function, first array [0] is function itself
    y2b = np.exp(-x2*x2/4)
    y2 = y2a*y2b

    y[x>=branch] = y2

    return y


def bortfeld(z, D100, R0, sigma, p=1.77, k=0.01394):
    """ Bortfeld function to approximate a Bragg curve.
    
    Parameters
    -----------
    :param z: depth in phantom in cm
    :param D100: approximate maximum Dose (height of peak)
    :param R0: bragg curve range in cm (distance to 80% D100 on distal side)
    :param sigma: sigma term, measure for peak width
    :param p: exponent of "Bragg-Kleeman rule" (default 1.77)
    :param k: scaling factor w/ dependence on epsilon, (default 0.01394) 
  
    Returns
    --------
    :returns:  D(z) - depth dose in depth z
    """
    
    return 0.65 * D100 * ( cyl_gauss( -1/p, (z-R0)/sigma ) + sigma*k*cyl_gauss( -1/p-1, (z-R0)/sigma ) )


def characterize_z_D_curve(z, D):
    """ Method that computes dose and range quantities from a given bragg curve
    
    Parameters
    -----------
    :param z: depth in phantom in cm
    :param D: dose at depth z
    
    Returns
    --------
    :returns: 
      - results (dict): Ranges to certain fractions of Dmax on distal (D) and proximal (P) side of peak. Also: FWHM, DFO(1090)/(2080)
    """
    
    results = {}

    # compute quantities
    D100_index = np.argmax(D)
    D100       = D[D100_index]
    R100       = z[D100_index]
    results.update({
        'D100': D100,
        'R100': R100
    })

    # split at peak index into proximal and distal part
    z_proximal    = z[:D100_index]
    dose_proximal = D[:D100_index]
    z_distal      = z[D100_index:]
    dose_distal   = D[D100_index:]

    R90P = z_proximal[np.argmin(np.abs(dose_proximal - 0.9 * D100))]
    R90D = z_distal  [np.argmin(np.abs(dose_distal   - 0.9 * D100))]
    R80P = z_proximal[np.argmin(np.abs(dose_proximal - 0.8 * D100))]
    R80D = z_distal  [np.argmin(np.abs(dose_distal   - 0.8 * D100))]
    R50P = z_proximal[np.argmin(np.abs(dose_proximal - 0.5 * D100))]
    R50D = z_distal  [np.argmin(np.abs(dose_distal   - 0.5 * D100))]
    R20D = z_distal  [np.argmin(np.abs(dose_distal   - 0.2 * D100))]
    R10D = z_distal  [np.argmin(np.abs(dose_distal   - 0.1 * D100))]
    results.update({
        'R90P': R90P,
        'R90D': R90D,
        'R80P': R80P,
        'R80D': R80D,
        'R50P': R50P,
        'R50D': R50D,
        'R20D': R20D,
        'R10D': R10D
    })

    FWHM    = R50D  - R50P
    DFO2080 = R20D  - R80D
    DFO1090 = R10D  - R90D
    results.update({
        'FWHM': FWHM,
        'DFO2080': DFO2080,
        'DFO1090': DFO1090,
    })

    return results


def bortfeld_for_odr(bortfeld_parameters, z):
    D100, R0, sigma, p, k = bortfeld_parameters
    return 0.65 * D100 * ( cyl_gauss( -1/p, (z-R0)/sigma ) + sigma*k*cyl_gauss( -1/p-1, (z-R0)/sigma ) )

def fitBP_odr(z, D, z_unc, D_unc, method='bortfeld', rel_resolution=0.01):
    """ Automated fit and characterization of a pragg curve.
    
    Parameters
    -----------
    :param z: depth in phantom in cm
    :param D: dose at depth z
    :param method: "bortfeld" for full fit with Bortfeld approximation. "spline" for fast and simple spline fit (default "bortfeld")
    :param rel_resolution: fraction of z step width for the fit function characterization for range quantities like R80. (default 0.01)
  
    Returns
    --------
    :returns:  D(z) - depth dose in depth z
    """

    # check for validity of relevant input arguments
    assert len(z) == len(D), f"z and D need to have same length but are len(z)={len(z)} and len(D)={len(D)}"
    assert method in ['spline', 'bortfeld'], f"method can only be 'spline' or 'bortfeld' but is {method}"

    # define some accuracy settings
    resolution = rel_resolution*np.min(np.diff(z))

    # fit spline with given precision to curve
    spline_func = interp1d(z, D, kind='cubic')
    z_spline    = np.linspace(min(z), max(z), round((max(z)-min(z)) / resolution ))
    quantities  = characterize_z_D_curve(z_spline, spline_func(z_spline))

    # return interpolation for reference as well
    quantities['spline_func'] = spline_func

    # if spline fit only, return already
    if method == 'spline':
        return quantities

    # use precomputed values for further computations using bortfeld fit
    if method == 'bortfeld':
        # create init parameters from
        p         = 1.77 # result from paper Fig. 1
        alpha     = 0.0022 # result from paper Fig. 1
        R0        = quantities['R80D']
        E0        = (R0/alpha)**(1/p) # paper: Eq. (4)
        sigmaMono = (0.012*R0**0.935) # paper: Eq. (18)
        sigmaE0   = 0.01*E0 # assumtion that Delta E will be small
        sigma     = np.sqrt(sigmaMono**2+sigmaE0**2*alpha**2*p**2*E0**(2*p-2)) # paper: Eq. (19)

        # normalization constant for fit
        A = quantities['D100']
        # normalization constant for second part of equation, depends on the epsilon from the original publication
        k = 0.01394

        
        beta0, _= fit_bortfeld(z, D, z_unc)

        function_model = odr.Model(bortfeld_for_odr)
        # mydata = odr.Data(z, D, wd=z_unc, we=D_unc)
        mydata = odr.RealData(z, D, sx=z_unc, sy=D_unc)
        myodr = odr.ODR(mydata, function_model, beta0=[A, R0, sigma, p, k])
        myoutput = myodr.run()
        
        myoutput.pprint()
        
        p = myoutput.beta
        c = myoutput.cov_beta

        # return for easy access
        quantities['bortfeld_fit_results'] = {var: {'nominal': nom, 'std': std} for var, nom, std in zip(['D100', 'R0', 'sigma', 'p', 'k'], p, np.diag(c))}

        # return parameter vector and cov matrix as well
        quantities['bortfeld_fit_p']       = p
        quantities['bortfeld_fit_cov']     = c
        print(f"Parameter uncertainties: {myoutput.sd_beta}")
        print("Parameter uncertainties over")

        chi_square = myoutput.sum_square
        print(f"Chi square: {chi_square}")
        degrees_of_freedom = len(z)
        chi_squared_reduced = chi_square / degrees_of_freedom
        print(f"Reduced chi square: {chi_squared_reduced}")



        true_uncertainties = myoutput.sd_beta
        # recalc some quantities if needed
        bortfeld_quantities = characterize_z_D_curve(z_spline, bortfeld(z_spline, *p))
        # overwrite results from spline fit
        quantities.update(bortfeld_quantities)

        return quantities, true_uncertainties, chi_squared_reduced


def fit_bortfeld(z_bins, on_axis_energies, on_axis_energies_uncertainties):
    bortfeld_fit = fitBP(z_bins, on_axis_energies, on_axis_energies_uncertainties)
    fit_parameters = bortfeld_fit['bortfeld_fit_p']
    fit_parameters_covariance = bortfeld_fit['bortfeld_fit_cov']
    fit_parameters_uncertainties = np.sqrt(np.diag(fit_parameters_covariance))
    return fit_parameters, fit_parameters_uncertainties

def fit_bortfeld_odr(z_bins, on_axis_energies, z_uncertainties, on_axis_energies_uncertainties):
    bortfeld_fit, true_uncertainties, chi_squared_reduced = fitBP_odr(z_bins, on_axis_energies, z_uncertainties, on_axis_energies_uncertainties)
    fit_parameters = bortfeld_fit['bortfeld_fit_p']
    fit_parameters_covariance = bortfeld_fit['bortfeld_fit_cov']
    return fit_parameters, fit_parameters_covariance, true_uncertainties, chi_squared_reduced

def find_peak_of_bortfeld(z_bins, bortfeld_parameters, points_per_bin=100):
    z_length = len(z_bins) * points_per_bin
    z_range = np.linspace(z_bins[0], z_bins[-1], z_length)
    bortfeld_output = bortfeld(z_range, *bortfeld_parameters)
    peak_argument = np.argmax(bortfeld_output)
    peak_z_position = z_range[peak_argument]
    return peak_z_position

def round_to_precision(number, precision):
    rounded_number = np.round(number / precision) * precision
    return rounded_number

def find_peak_position_uncertainty(z_bins, bortfeld_parameters, bortfeld_parameter_uncertainties, points_per_bin=1000, number_of_stds=1):
    best_fit_peak_argument, best_fit_peak = find_peak_of_bortfeld(z_bins, bortfeld_parameters, points_per_bin=points_per_bin)
    lower_bound_parameters = bortfeld_parameters - number_of_stds*bortfeld_parameter_uncertainties
    upper_bound_parameters = bortfeld_parameters + number_of_stds*bortfeld_parameter_uncertainties
    all_parameter_combinations = list(product(*zip(lower_bound_parameters, upper_bound_parameters)))
    possible_peak_positions = np.empty((len(all_parameter_combinations)))
    for count, parameter_combination in enumerate(all_parameter_combinations):
        _, peak_position = find_peak_of_bortfeld(z_bins, parameter_combination, points_per_bin=points_per_bin)
        possible_peak_positions[count] = peak_position
    best_fit_z_bin_argument = math.ceil(best_fit_peak_argument / points_per_bin)
    z_bin_width = z_bins[best_fit_z_bin_argument] - z_bins[best_fit_z_bin_argument - 1]
    
    uncertainty_order = z_bin_width / points_per_bin

    lower_peak = np.min(possible_peak_positions)
    upper_peak = np.max(possible_peak_positions)
    lower_bound = best_fit_peak - lower_peak
    lower_bound = round_to_precision(lower_bound, uncertainty_order)
    upper_bound = upper_peak - best_fit_peak
    upper_bound = round_to_precision(upper_bound, uncertainty_order)
    return [lower_bound, upper_bound]


def find_range(z_bins, bortfeld_parameters, factor_of_peak=0.5, points_per_bin=1000):
    if factor_of_peak <= 0:
        raise Exception("Factor of peak must be positive.")
    if factor_of_peak >= 1:
        raise Exception("Factor of peak must be less than 1.")
    z_length = len(z_bins) * points_per_bin
    z_range = np.linspace(z_bins[0], z_bins[-1], z_length)
    heights = bortfeld(z_range, *bortfeld_parameters)

    peak_position = find_peak_of_bortfeld(z_bins, bortfeld_parameters, points_per_bin=points_per_bin)
    peak_height = bortfeld(peak_position, *bortfeld_parameters)
    half_peak_height = peak_height * factor_of_peak

    range_argument = np.where(heights > half_peak_height)[0][-1]
    range = z_range[range_argument]
    return range


def find_uncertainty_in_range(z_bins, bortfeld_parameters, bortfeld_parameter_uncertainties, factor_of_peak=0.5, points_per_bin=1000, number_of_stds=1):
    best_fit_range_argument, best_fit_range = find_range(z_bins, bortfeld_parameters, factor_of_peak=factor_of_peak, points_per_bin=points_per_bin)
    lower_bound_parameters = bortfeld_parameters - number_of_stds*bortfeld_parameter_uncertainties
    upper_bound_parameters = bortfeld_parameters + number_of_stds*bortfeld_parameter_uncertainties
    all_parameter_combinations = list(product(*zip(lower_bound_parameters, upper_bound_parameters)))
    possible_range_positions = np.empty((len(all_parameter_combinations)))
    for count, parameter_combination in enumerate(all_parameter_combinations):
        _, range = find_range(z_bins, parameter_combination, factor_of_peak=factor_of_peak, points_per_bin=points_per_bin)
        possible_range_positions[count] = range

    best_fit_z_bin_argument = math.ceil(best_fit_range_argument / points_per_bin)
    z_bin_width = z_bins[best_fit_z_bin_argument] - z_bins[best_fit_z_bin_argument - 1]
    uncertainty_order = z_bin_width / points_per_bin

    lower_range = np.min(possible_range_positions)
    upper_range = np.max(possible_range_positions)

    lower_bound = best_fit_range - lower_range
    lower_bound = round_to_precision(lower_bound, uncertainty_order)
    upper_bound = upper_range - best_fit_range
    upper_bound = round_to_precision(upper_bound, uncertainty_order)

    return [lower_bound, upper_bound]

def calculate_chi_squared(data_values, data_uncertainties, fit_values):
    weighted_difference_squared = ((data_values - fit_values) / data_uncertainties)**2
    chi_squared = np.sum(weighted_difference_squared)
    return chi_squared

def calculate_chi_squared_for_bortfeld_fit(bins, fit_parameters):
    fit_values = bortfeld(bins, *fit_parameters)
    bin_uncertainties = np.sqrt(bins)
    chi_squared = calculate_chi_squared(bins, bin_uncertainties, fit_values)
    degrees_of_freedom = len(bins) - len(fit_parameters)
    reduced_chi_squared = chi_squared / degrees_of_freedom
    return chi_squared, reduced_chi_squared, degrees_of_freedom


########### New uncertainty calculation paradigm ################################

def partial_function(func: callable, free_param_index: int, fixed_values):
    """
    Create a partial function by fixing all parameters except the one at free_param_index.
    `fixed_values` should be a list of values with None at the free_param_index position.
    """
    def wrapper(free_arg):
        args = fixed_values[:]
        args[free_param_index] = free_arg
        return func(args)
    return wrapper

def central_finite_difference(func: Callable, x):
    """
    Compute the central finite difference of a function at a given point.
    We need to evaluate the gradient about the best fit Bortfeld parameters
    """
    epsilon = np.finfo(float).eps # Get machine epsilon
    h = epsilon ** (1/3) * max(abs(x), 1.0)  # Optimal for central difference
    return (func(x + h) - func(x - h)) / (2 * h)


def multivariate_delta_method_for_bortfeld_derived_quantity(derived_quantity: Callable, fit_parameters, fit_parameter_covariance):
    
    grad_derived_quantities = []
    for index, param in enumerate(fit_parameters):
        partial_fit_parameters = fit_parameters[:]
        partial_fit_parameters[index] = None
        partial_derived_quantity = partial_function(derived_quantity, index, partial_fit_parameters)
        grad_derived_quantities.append(central_finite_difference(partial_derived_quantity, param))
        
    grad_derived_quantities = np.array(grad_derived_quantities)
    print(f"{grad_derived_quantities=}")
    
    derived_quantity_variance = grad_derived_quantities.T @ fit_parameter_covariance @ grad_derived_quantities
    print(f"{derived_quantity_variance=}")
    return np.sqrt(derived_quantity_variance)
    
def compute_error_on_bortfeld_peak(distances, fit_parameters, fit_parameter_covariance):
    func_with_distances_populated = partial(find_peak_of_bortfeld, distances)
    return multivariate_delta_method_for_bortfeld_derived_quantity(func_with_distances_populated, fit_parameters, fit_parameter_covariance)

def compute_error_on_mean_range(distances, fit_parameters, fit_parameter_covariance):
    func_with_distances_populated = partial(find_range, distances)
    return multivariate_delta_method_for_bortfeld_derived_quantity(func_with_distances_populated, fit_parameters, fit_parameter_covariance)
