import numpy as np
from typing import List


def normal_addition_in_quadrature(contributing_quantity_uncertainties: List[float]):
  squared_sum = 0
  for count in range(len(contributing_quantity_uncertainties)):
    squared_sum += contributing_quantity_uncertainties[count]**2
  return np.sqrt(squared_sum)


def fractional_addition_in_quadrature(contributing_quantity_values: List[float], contributing_quantity_uncertainties: List[float],
                                      final_quantity_value: float):
  squared_sum = 0
  for count in range(len(contributing_quantity_uncertainties)):
    squared_sum += (contributing_quantity_uncertainties[count] / contributing_quantity_values[count])**2
  return final_quantity_value * np.sqrt(squared_sum)


def calculate_uncertainty_on_dot_product(vector_1: np.ndarray[float], vector_2: np.ndarray[float],
                                         vector_1_uncertainty: np.ndarray[float], 
                                         vector_2_uncertainty: np.ndarray[float]):
  """
  Should validate that the vectors have the same dimensions.
  """
  summation = 0 
  for i in range(len(vector_1)):
    summation += (vector_2[i] * vector_1_uncertainty[i])**2 + (vector_1[i] * vector_2_uncertainty[i])**2
  return np.sqrt(summation)


def calculate_uncertainty_on_cross_product(vector_1: np.ndarray[float], vector_2: np.ndarray[float],
                                           vector_1_uncertainty: np.ndarray[float], 
                                           vector_2_uncertainty: np.ndarray[float]):
  a_1, a_2, a_3 = vector_1
  unc_a_1, unc_a_2, unc_a_3 = vector_1_uncertainty
  b_1, b_2, b_3 = vector_2
  unc_b_1, unc_b_2, unc_b_3 = vector_2_uncertainty
  
  # Component 1
  component_1_term_1 = a_2 * b_3
  component_1_term_1_unc = fractional_addition_in_quadrature([a_2, b_3], [unc_a_2, unc_b_3], component_1_term_1)
  component_1_term_2 = a_3 * b_2
  component_1_term_2_unc = fractional_addition_in_quadrature([a_3, b_2], [unc_a_3, unc_b_2], component_1_term_2)
  component_1_unc = normal_addition_in_quadrature([component_1_term_1_unc, component_1_term_2_unc])
  # Component 2
  component_2_term_1 = a_3 * b_1
  component_2_term_1_unc = fractional_addition_in_quadrature([a_3, b_1], [unc_a_3, unc_b_1], component_2_term_1)
  component_2_term_2 = a_1 * b_3
  component_2_term_2_unc = fractional_addition_in_quadrature([a_1, b_3], [unc_a_1, unc_b_3], component_2_term_2)
  component_2_unc = normal_addition_in_quadrature([component_2_term_1_unc, component_2_term_2_unc])
  # Component 3
  component_3_term_1 = a_1 * b_2
  component_3_term_1_unc = fractional_addition_in_quadrature([a_1, b_2], [unc_a_1, unc_b_2], component_3_term_1)
  component_3_term_2 = a_2 * b_1
  component_3_term_2_unc = fractional_addition_in_quadrature([a_2, b_1], [unc_a_2, unc_b_1], component_3_term_2)
  component_3_unc = normal_addition_in_quadrature([component_3_term_1_unc, component_3_term_2_unc])
  
  return np.array([component_1_unc, component_2_unc, component_3_unc])


def calculate_uncertainty_in_vector_magnitude(vector, unc_vector):
  """
  Both arguments should be 3 dimensional np arrays.
  """
  vector_magnitude = np.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
  unc_vector_magnitude = np.sqrt((vector[0] * unc_vector[0])**2 + (vector[1] * unc_vector[1])**2 + (vector[2] * unc_vector[2])**2) / vector_magnitude
  return unc_vector_magnitude

