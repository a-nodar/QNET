#!/usr/bin/env python

from __future__ import division
from collections import defaultdict    
from qnet.algebra.circuit_algebra import *
import numpy as np

def _coeff_term(expr):
    if isinstance(expr, ScalarTimesOperator):
        return expr.coeff, expr.term
    else:
        return 1, expr
    
def get_coeffs(expr, expand=False, epsilon = 0.):
    """
    Create a dictionary with all Operator terms of the expression
    (understood as a sum) as keys and their coefficients as values.

    The returned object is a defaultdict that return 0. if a term/key 
    doesn't exist.
    """
    if expand: 
        expr = expr.expand()
    ret = defaultdict(float)
    operands = expr.operands if isinstance(expr, OperatorPlus) else [expr]
    for e in operands:
        c, t = _coeff_term(e)
        try:
            if abs(complex(c)) < epsilon:
                continue
        except:
            pass
        ret[t] += c
    return ret

def model_matrices(slh, dynamic_input_ports, apply_kerr_diagonal_correction=True, epsilon = 0., return_eoms=False):
    """
    Return the matrices necessary to carry out a semi-classical simulation 
    of the SLH system driven by some dynamic inputs.

    Params
    ------
    slh: SLH object

    dynamic_input_ports: python dict {port_index: input_name_str,...}

    apply_kerr_diagonal_correction: bool that specifies whether there should be an 
                                    effective detuning of 2 \chi for every kerr-cavity.

    epsilon: for non-zero epsilon (and a numerical coefficient slh) remove 
             expressions with coefficents smaller than epsilon.

    return_eoms: Whether to also return the symbolic e.o.m.'s as well as the output processes.
    
    Returns
    -------
    A tuple (A, B, C, D, A_kerr, B_input, D_input, u_c, U_c[, eoms, dA'])

    A: coupling of modes to each other
    B: coupling of external input fields to modes
    C: coupling of internal modes to output
    D: coupling of external input fields to output fields

    A_kerr: kerr-type coupling between modes
    B_input: coupling of dynamic inputs to modes
    D_input: coupling of dynamic inputs to external output fields
    u_c: constant coherent input driving to modes
    U_c: constant coherent input contribution to output field

    Optional
    --------

    eoms: symbolic QSDEs for the internal modes
    dA': symbolic expression for the output fields

    The overall SDE is then:
    da_t/dt = (A * a_t - 2i (A_kerr * (a_t (*) a_t^*)) (*) a_t + u_c + B_input * u_t) + B * dA_t/dt
    dA'_t/dt = (C * a_t + U_c + D_input * u_t) + D * dA_t/dt

    Here A * b is a matrix product, whereas a (*) b is an element-wise
    product of two vectors.  It is assumed that all degrees of freedom
    are cavities with their only non-linearity being of the Kerr-type,
    i.e. either self coupling H_kerr = a^*a^* a a or cross-coupling
    H_kerr = a^*a b^*b.
    """

    # the different degrees of freedom
    modes = sorted(slh.space.local_factors())
    
    # various dimensions
    ncav = len(modes)
    cdim = slh.cdim
    ninputs = len(dynamic_input_ports)
    
    # initialize the matrices
    A = np.zeros((ncav, ncav), dtype=object)
    B = np.zeros((ncav, cdim), dtype=object)
    C = np.zeros((cdim, ncav), dtype=object)
    D = slh.S
    A_kerr = np.zeros((ncav, ncav), dtype=object)
    B_input = np.zeros((ncav, ninputs), dtype=object)
    D_input = np.zeros((cdim, ninputs), dtype=object)
    u_c = np.zeros(ncav, dtype=object)
    U_c = np.zeros(cdim, dtype=object)
    
    # make symbols for the external field modes
    noises = [OperatorSymbol('dA/dt_{{{}}}'.format(n), TrivialSpace) for n in range(cdim)]
    
    # make symbols for the dynamic inputs
    inputs = [OperatorSymbol('u_{{{}}}'.format(u_name), TrivialSpace) for  
               n, u_name in sorted(dynamic_input_ports.items())]
    
    inputs_extended = [0] * cdim
    for ii, n in zip(inputs, sorted(dynamic_input_ports.keys())):
        inputs_extended[n] = ii

    # feed in the dynamic inputs
    slh_input = slh.coherent_input(*inputs_extended).expand().simplify_scalar()
    
    print("computing QSDEs")
    # compute the QSDEs for the internal operators
    eoms = [slh_input.symbolic_heisenberg_eom(Destroy(s), noises=noises).expand().simplify_scalar() for s in modes]
    
    
    print("Extracting matrices")
    # use the coefficients to generate A, B matrices
    for jj, sjj in enumerate(modes):
        coeffsjj = get_coeffs(eoms[jj], epsilon=epsilon)
        for kk, skk in enumerate(modes):
            A[jj, kk] = coeffsjj[Destroy(skk)]
            A_kerr[jj, kk] = coeffsjj[Create(skk) * Destroy(skk) * Destroy(sjj)]/-2j
        for kk, dAkk in enumerate(noises):
            B[jj, kk] = coeffsjj[dAkk]
        for kk, u_kk in enumerate(inputs):
            if inputs == 0:
                continue
            B_input[jj,kk] = coeffsjj[u_kk]
        u_c[jj] = coeffsjj[IdentityOperator]
    
    
    # use the coefficients in the L vector to generate the C, D
    # matrices
    for jj, Ljj in enumerate(slh_input.L.matrix[:,0]):
        coeffsjj = get_coeffs(Ljj)
        for kk, skk in enumerate(modes):
            C[jj,kk] = coeffsjj[Destroy(skk)]
        U_c[jj] = coeffsjj[IdentityOperator]
        
        for kk, u_kk in enumerate(inputs):
            D_input[jj, kk] = coeffsjj[u_kk]
    

    if return_eoms:
        # compute output processes
        dAps =  (slh_input.S * Matrix([noises]).T + slh_input.L).expand().simplify_scalar()
        return A, B, C, D, A_kerr, B_input, D_input, u_c, U_c, eoms, dAps
    
    return A, B, C, D, A_kerr, B_input, D_input, u_c, U_c


def model_matrices_complex(*args, **kwargs):
    "Same as model_matrices() but tries to convert all output to purely numerical matrices"
    matrices = model_matrices(*args, **kwargs)
    if len(matrices) <= 9:
        return [arr.astype(complex) for arr in matrices]
    else:
        return [arr.astype(complex) for arr in matrices[:9]] + list(matrices[9:])
        

def model_matrices_symbolic(*args, **kwargs):
    "Same as model_matrices() but converts all output to Matrix() objects."
    matrices = model_matrices(*args, **kwargs)
    if len(matrices) <= 9:
        return [Matrix(arr) for arr in matrices]
    else:
        return [Matrix(arr) for arr in matrices[:9]] + list(matrices[9:])
        


def substitute_into_symbolic_model_matrices(model_matrices, params):
    
    return [m.substitute(params).matrix.astype(complex) for m in model_matrices[:9]] + list(model_matrices[9:])


def prepare_sde(numeric_model_matrices, input_fn):
    """
    Compute the SDE functions f, g (see euler_mayurama docs) for the model matrices.

    The overall SDE is:
    da_t/dt = (A * a_t - 2i (A_kerr * (a_t (*) a_t^*)) (*) a_t + u_c + B_input * u_t) + B * dA_t/dt
    dA'_t/dt = (C * a_t + U_c + D_input * u_t) + D * dA_t/dt
    """
    A, B, C, D, A_kerr, B_input, D_input, u_c, U_c = numeric_model_matrices[:9]
    B_over_2 = B/2.
    u_c = u_c.ravel()

    def f(a, t):
        return A.dot(a) - 2j * (A_kerr.dot(a.conjugate() * a)) * a + u_c + B_input.dot(input_fn(t))
    
    def g(a, t):
        return B_over_2
    
    return f, g
