# -*- coding: utf-8 -*-
"""Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2020 Caleb Bell
<Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


.. contents:: :local:


"""
from __future__ import division
from fluids.numerics import trunc_exp
from math import exp, log, sqrt
__all__ = ['lemmon2000_air_A0', 'lemmon2000_air_dA0_dtau',
           'lemmon2000_air_d2A0_dtau2', 'lemmon2000_air_d3A0_dtau3',
           'lemmon2000_air_d4A0_dtau4',
           'lemmon2000_air_Ar', 'lemmon2000_air_dAr_dtau',
           'lemmon2000_air_d2Ar_dtau2']

# Get a good, fast variant of lemmon (2004) in here

# For values of tau above this, log(exp(87.31279*tau) + 2/3) reduces to 87.31279*tau in double precision
TAU_MAX_EXP_87 = 0.4207493606569795

def lemmon2000_air_A0(tau, delta):
    r'''Calculates the ideal gas Helmholtz energy of air according to Lemmon 
    (2000).
    
    .. math::
        \phi^\circ = \ln \delta + \sum_{i=1}^5 N_i\tau^{i-4} + N_6\tau^{1.5}
        + N_7\ln \tau + N_8\ln[1-\exp(-N_{11}\tau)] + N_9\ln[1-\exp(-N_{12}\tau)]
        + N_{10}\ln[2/3 + \exp(N_{13}\tau)]

    Parameters
    ----------
    tau : float
        Dimensionless temperature, (132.6312 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    A0 : float
        Ideal gas dimensionless Helmholtz energy A0/(RT) [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_A0(132.6312/200.0, 13000/10447.7)
    -14.65173785639
    '''
    tau_inv = 1.0/tau
    
#    exp0_00001 = exp(0.00001*tau)
    A0 =  (-0.00019536342*tau*sqrt(tau) + 17.275266575*tau + tau_inv*(tau_inv*(6.057194e-8*tau_inv 
            - 0.0000210274769) - 0.000158860716) + log(delta) + 2.490888032*log(tau)
    
            # These two logs both fail for tau < 1e-18, can be truncated but should not be necessary.
            + 0.791309509*log(1.0 - exp(-25.36365*tau)) + 0.212236768*log(1.0 - exp(-16.90741*tau)) 
            - 13.841928076)
    if tau < TAU_MAX_EXP_87:
        A0 -= 0.197938904*log(exp(87.31279*tau) + (2.0/3.0))
    else:
        A0 -= 17.282597957782162*tau # 17.282... = 87.31279*0.197938904
    return A0


def lemmon2000_air_dA0_dtau(tau, delta):
    r'''Calculates the first temperature derivative of ideal gas Helmholtz
    energy of air according to Lemmon (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (132.6312 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    dA0_dtau : float
        First derivative of `A0/RT` Ideal gas dimensionless Helmholtz energy
         with respect to `tau` [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_dA0_dtau(132.6312/200.0, 13000/10447.7)
    3.749095669249
    '''
    tau_inv = 1.0/tau
    dA0_dtau = (-0.00029304513*sqrt(tau) + tau_inv*(-tau_inv*(tau_inv*(1.8171582e-7*tau_inv 
            - 0.0000420549538) - 0.000158860716) + 2.490888032) + 17.275266575)
    try:
        # limit as tau gets high goes to zer0
        x0 = exp(87.31279*tau)
        dA0_dtau -= 17.282597957782162*x0/(x0 + (2.0/3.0))
    except:
        dA0_dtau -= 17.282597957782162
    try:
        # Limit is zero
        dA0_dtau += 20.0704974279478492/(exp(25.36365*tau) - 1.0)
    except:
        pass
    try:
        dA0_dtau += 3.58837405365087969/(exp(16.90741*tau) - 1.0)
    except:
        pass
    return dA0_dtau
    
    
def lemmon2000_air_d2A0_dtau2(tau, delta):
    r'''Calculates the second temperature derivative of ideal gas Helmholtz
    energy of air according to Lemmon (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (126.192 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    d2A0_dtau2 : float
        Second derivative of `A0/RT` Ideal gas dimensionless Helmholtz energy
         with respect to `tau` [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_d2A0_dtau2(132.6312/200.0, 13000/10447.7)
    -5.66675499015
    '''
    tau_inv = 1.0/tau
    d2A0_dtau2 = (-0.000146522565*sqrt(tau_inv) + tau_inv*(tau_inv*(tau_inv*(
            7.2686328e-7*tau_inv - 0.0001261648614) - 0.000317721432) 
            - 2.490888032)*tau_inv)
    
    if tau < 3.0:
        # 87.31279 Begins to have an impact a little under 0.5, others at 2.5 - set to 3 for safety
        x0 = exp(87.31279*tau)
        
        a = x0 + 2.0/3.0
        b = x0*(4.0/3.0 + x0) + 4.0/9.0
        d2A0_dtau2 += 1508.99184614226283*x0*(a*x0 - b)/(a*b)
                
        x0 = exp(25.36365*tau)
        a = (x0 - 1.0)
        b = x0*(x0 - 2.0) + 1.0
        d2A0_dtau2 -= 509.061072088369485*(a+b)/(a*b)
        
        x0 = exp(16.90741*tau)
        a = x0 - 1.0
        b = x0*(x0 - 2.0) + 1.0
        d2A0_dtau2 -= 60.670111358437417*(a+b)/(a*b)
    return d2A0_dtau2
    
def lemmon2000_air_d3A0_dtau3(tau, delta):
    r'''Calculates the third temperature derivative of ideal gas Helmholtz
    energy of air according to Lemmon (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (126.192 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    d3A0_dtau3 : float
        Third derivative of `A0/RT` Ideal gas dimensionless Helmholtz energy
         with respect to `tau` [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_d3A0_dtau3(132.6312/200.0, 13000/10447.7)
    17.10538866838
    '''
    tau_inv = 1.0/tau
    d3A0_dtau3 = (tau_inv*(0.0000732612825*sqrt(tau_inv) + tau_inv*(-tau_inv*(tau_inv*(
            3.6343164e-6*tau_inv - 0.0005046594456) - 0.000953164296) + 4.981776064)*tau_inv))
    d3A0_dtau3_base = d3A0_dtau3
    
    if tau < 2.5:
        x0 = exp(16.90741*tau)
        x1 = exp(25.36365*tau)
        x3 = x0*x0
        
        x2 = exp(87.31279*tau)
        x4 = x2*x2
        x5 = x2*x2*x2
        d3A0_dtau3 += (-131754.288173931709*x2/(x2 + (2.0/3.0))
                + 395262.864521795127*x4/(1.333333333333333333*x2 + x4 + 0.444444444444444864) 
                - 263508.576347863418*x5/(1.333333333333333333*x2 + 2.0*x4 + x5 + 0.296296296296296668))
                
        d3A0_dtau3 += (25823.2937221483444/(3.0*x1 - 3.0*x1*x1 + x1*x1*x1 - 1.0) 
                            + 38734.9405832225166/(-2.0*x1 + x1*x1 + 1.0) 
                            + 12911.6468610741722/(x1 - 1.0))
        
        d3A0_dtau3 += (+ 2051.54889496551641/(3.0*x0 - 3.0*x3 + x0*x0*x0 - 1.0)
                        + 3077.32334244827462/(-2.0*x0 
                        + x3 + 1.0)  + 1025.77444748275821/(x0 - 1.0))
    return d3A0_dtau3

def lemmon2000_air_d4A0_dtau4(tau, delta):
    r'''Calculates the fourth temperature derivative of ideal gas Helmholtz
    energy of air according to Lemmon (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (132.6312 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    d4A0_dtau4 : float
        Fourth derivative of `A0/RT` Ideal gas dimensionless Helmholtz energy
         with respect to `tau` [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_d4A0_dtau4(126.192/200.0, 13000/10447.7)
    -94.815532727
    '''
    tau_inv = 1.0/tau
    tau_inv2 = tau_inv*tau_inv
    d4A0_dtau4 = (-tau_inv2*(0.00010989192375*sqrt(tau_inv) - tau_inv2*(tau_inv*(
            tau_inv*(0.0000218058984*tau_inv - 0.002523297228)
            - 0.003812657184) - 14.945328192)))
    if tau < 0.4:
        x2 = exp(87.31279*tau)
        x5 = x2*x2
        x8 = x2*x2*x2
        x9 = x2*x2*x2*x2
        d4A0_dtau4 += 11503834.4949299842*x2*(-1.0/(x2 + 2.0/3.0) #1
        + x2*(7.0/((4.0/3.0)*x2 + x5 + (4.0/9.0))  #7
        - x2*(12.0/((4.0/3.0)*x2 + 2.0*x5 + x8 + (8.0/27.0)) #12
        + 6.0*x2/((-32.0/27.0)*x2 - (8.0/3.0)*(x5 +x8) - x9 - 16.0/81.0)  #6
        )))
    if tau < 2.0:
        x1 = exp(25.36365*tau)
        d4A0_dtau4 -= 327486.491907883901*(6.0/(x1*(x1*(x1*(x1 - 4.0) + 6.0) - 4.0) + 1.0) #6
        + 12.0/(x1*(x1*(x1 - 3.0) + 3.0) - 1.0) #12
        + 7.0/(x1*(x1 - 2.0) + 1.0) # 7
         + 1.0/(x1 - 1.0))
    if tau < 2.875:
        x0 = exp(16.90741*tau)
        d4A0_dtau4 += 17343.1891511144604*(6.0/(-x0*(x0*(x0*(x0 - 4.0) + 6.0) - 4.0) -1.0) #6
        - 12.0/(x0*(x0*(x0 - 3.0) + 3.0) - 1.0)  # 12
        - 7.0/(1.0 + x0*(x0 - 2.0)) # 7
        - 1.0/(x0 - 1.0)) # 1
    return d4A0_dtau4



def lemmon2000_air_Ar(tau, delta):
    r'''Calculates the residual Helmholtz energy of air according to Lemmon 
    (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (132.6312 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    Ar : float
        Residual dimensionless Helmholtz energy Ar/(RT) [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_Ar(132.6312/200.0, 13000/10447.7)
    -0.34683017661
    >>> lemmon2000_air_Ar(0.36842, 0.15880050154579475)
    0.0047988122806
    '''
    tau_100 = tau**0.01
    delta2 = delta*delta
    delta3 = delta*delta2
    delta4 = delta2*delta2
    delta5 = delta*delta4
    delta6 = delta2*delta4
    taurt2 = sqrt(tau)
    taurt4 = sqrt(taurt2)
    tau2 = tau*tau
    tau3 = tau*tau2
    tau6 = tau3*tau3
    tau12 = tau6*tau6
    tau2_100 = tau_100*tau_100
    tau4_100 = tau2_100*tau2_100
    tau5_100 = tau_100*tau4_100
    tau10_100 = tau5_100*tau5_100
    tau15_100 = tau5_100*tau10_100
    tau8_100 = tau4_100*tau4_100
    tau16_100 = tau8_100*tau8_100
    tau20_100 = tau4_100*tau16_100
    tau32_100 = tau16_100*tau16_100
    tau33_100 = tau_100*tau32_100
    tau64_100 = tau32_100*tau32_100
    tau80_100 = tau16_100*tau64_100
    tau40_100 = tau20_100*tau20_100
    tau97_100 = tau33_100*tau64_100
    tau45_100 = tau5_100*tau40_100
    tau90_100 = tau45_100*tau45_100
    tau160_100 = tau80_100*tau80_100
    tau320_100 = tau160_100*tau160_100
    x0 = delta + delta3
    x1 = delta6*taurt4
    return ((tau3*(0.0148287891978000005*delta*taurt2 - 0.00938782884667000057*delta3*tau12)*exp(delta + delta2)
             - (0.146629609712999986*delta*tau320_100*tau40_100 + 0.031605587982100003*delta3*tau6
                - 0.000233594806141999996*delta5*tau3*x1)*exp(x0) - (0.101365037911999994*delta*tau160_100 
            + 0.17381369096999999*delta3*tau80_100 + 0.0472103183731000034*delta5*tau15_100*tau80_100 
            + 0.0122523554252999996*tau*x1)*exp(delta2 + delta3) + (0.713116392079000017*delta*tau33_100 
            - 1.61824192067000006*delta*tau4_100*tau97_100 + 0.118160747228999996*delta + 0.0714140178971000017*delta2 
            + 0.134211176704000013*delta3*tau15_100 - 0.0865421396646000041*delta3 - 0.042053322884200002*delta4*tau20_100 
            + 0.0349008431981999989*delta4*tau2_100*tau33_100 + 0.0112626704218000001*delta4
            + 0.000164957183185999979*delta6*tau45_100*tau90_100)*exp(delta2 + x0))*exp(-delta - delta2 - delta3))
    
    
def lemmon2000_air_dAr_dtau(tau, delta):
    r'''Calculates the first derivative of residual Helmholtz energy of air 
    with respect to tau according to Lemmon (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (132.6312 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    dAr_dtau : float
        First derivative of residual dimensionless Helmholtz energy Ar/(RT)
        with respect to tau, [-]

    Notes
    -----
    The cost of this function is 1 power, 3 exp, 2 sqrt, 2 divisions.
            
    Examples
    --------
    >>> lemmon2000_air_dAr_dtau(132.6312/200.0, 13000/10447.7)
    -1.8112257495223263
    '''
    delta2 = delta*delta
    delta3 = delta*delta2
    delta4 = delta2*delta2
    delta5 = delta*delta4
    delta6 = delta2*delta4
    tau_inv = 1.0/tau
    taurt2 = sqrt(tau)
    taurt4 = sqrt(taurt2)
    tau2 = tau*tau
    tau4 = tau2*tau2
    tau5 = tau*tau4
    tau10 = tau5*tau5
    tau_100 = tau**0.01
    tau2_100 = tau_100*tau_100
    tau4_100 = tau2_100*tau2_100
    tau8_100 = tau4_100*tau4_100
    tau16_100 = tau8_100*tau8_100
    tau32_100 = tau16_100*tau16_100
    tau33_100 = tau_100*tau32_100
    tau20_100 = tau4_100*tau16_100
    tau40_100 = tau20_100*tau20_100
    tau65_100 = tau32_100*tau33_100
    tau130_100 = tau65_100*tau65_100
    tau_inv_100 = 1.0/tau_100
    tau_inv2_100 = tau_inv_100*tau_inv_100
    tau_inv4_100 = tau_inv2_100*tau_inv2_100
    tau_inv5_100 = tau_inv_100*tau_inv4_100
    tau_inv8_100 = tau_inv4_100*tau_inv4_100
    tau_inv16_100 = tau_inv8_100*tau_inv8_100
    tau_inv20_100 = tau_inv4_100*tau_inv16_100
    tau_inv32_100 = tau_inv16_100*tau_inv16_100
    tau_inv64_100 = tau_inv32_100*tau_inv32_100
    tau_inv65_100 = tau_inv_100*tau_inv64_100
    tau_inv80_100 = tau_inv16_100*tau_inv64_100
    tau_inv10_100 = tau_inv5_100*tau_inv5_100
    tau_inv40_100 = tau_inv20_100*tau_inv20_100
    x0 = exp(-delta2)
    x1 = exp(-delta)
    x2 = delta6*taurt4
    x3 = exp(-delta3)
    return (-0.527866594966799996*delta*tau130_100*tau130_100*x0 + 0.0519007621922999984*delta*tau2*taurt2*x3 
            - 0.162184060659199991*delta*tau20_100*tau40_100*x1 - 1.63442433987669999*delta*tau_100 
            + 0.235328409386070025*delta*tau_inv2_100*tau_inv65_100 - 0.14081743270005001*delta3*tau10*tau4*x3 
            - 0.189633527892600018*delta3*tau5*x0 - 0.139050952775999992*delta3*tau_inv20_100*x1
            + 0.0201316765056000005*delta3*tau_inv5_100*tau_inv80_100 + 0.0122152951193699993*delta4*tau_inv65_100
            - 0.0084106645768400011*delta4*tau_inv80_100 + 0.000759183119961499907*delta5*tau2*x0*x2
            - 0.0448498024544450036*delta5*tau_inv5_100*x1 + 0.00022269219730110002*delta6*tau2_100*tau33_100 
            - 0.0153154442816249986*x1*x2)

def my_exp(x):
    from math import exp
    print([x])
    return exp(x)

def lemmon2000_air_d2Ar_dtau2(tau, delta):
    r'''Calculates the second derivative of residual Helmholtz energy of air 
    with respect to tau according to Lemmon (2000).
    
    Parameters
    ----------
    tau : float
        Dimensionless temperature, (132.6312 K)/T [-]
    delta : float
        Dimensionless density, rho/(10447.7 mol/m^3), [-]

    Returns
    -------
    d2Ar_dtau2 : float
        Second derivative of residual dimensionless Helmholtz energy Ar/(RT)
        with respect to tau, [-]

    Notes
    -----
            
    Examples
    --------
    >>> lemmon2000_air_d2Ar_dtau2(132.6312/200.0, 13000/10447.7)
    -0.7632109061747537
    '''
    delta2 = delta*delta
    delta3 = delta*delta2
    delta4 = delta2*delta2
    delta5 = delta*delta4
    tau_inv = 1.0/tau
    taurt2 = sqrt(tau)
    tau_invrt2 = sqrt(tau_inv)
    tau_invrt4 = sqrt(tau_invrt2)
    tau2 = tau*tau
    tau4 = tau2*tau2
    tau8 = tau4*tau4
    tau12 = tau4*tau8
    tau_inv_100 = tau_inv**0.0100000000000000002
    tau_inv2_100 = tau_inv_100*tau_inv_100
    tau_inv4_100 = tau_inv2_100*tau_inv2_100
    tau_inv8_100 = tau_inv4_100*tau_inv4_100
    tau_inv16_100 = tau_inv8_100*tau_inv8_100
    tau_inv32_100 = tau_inv16_100*tau_inv16_100
    tau_inv40_100 = tau_inv8_100*tau_inv32_100
    tau_inv33_100 = tau_inv_100*tau_inv32_100
    tau_inv65_100 = tau_inv32_100*tau_inv33_100
    tau_inv66_100 = tau_inv33_100*tau_inv33_100
    tau_inv99_100 = tau_inv33_100*tau_inv66_100
    tau_inv105_100 = tau_inv40_100*tau_inv65_100
    tau_inv80_100 = tau_inv40_100*tau_inv40_100
    tau_inv165_100 = tau_inv66_100*tau_inv99_100
    tau_inv20_100 = tau_inv4_100*tau_inv16_100
    tau_inv160_100 = tau_inv80_100*tau_inv80_100
    tau_inv24_100 = tau_inv8_100*tau_inv16_100
    tau_inv104_100 = tau_inv24_100*tau_inv80_100
    x0 = delta + delta3
    x1 = delta2*tau_inv80_100
    exp = my_exp
    return (-delta*(tau*(1.9714440578007002*delta2*tau12 - 0.129751905480749996*taurt2)*exp(delta + delta2) 
            + (0.948167639463000089*delta2*tau4 - 0.00170816201991337503*delta5**2*tau*sqrt(taurt2)
            + 1.37245314691368003/(tau_inv80_100*tau_inv80_100))*exp(x0) - (0.00224249012272225226*delta4*tau_inv105_100 
            - 0.00382886107040624965*delta5*tau_invrt2*tau_invrt4 + 0.0278101905551999921*tau_inv40_100*x1
            - 0.0973104363955200058*tau_inv40_100)*exp(delta2 + delta3) 
            + (-0.00672853166147200157*delta3*tau_inv160_100*tau_inv20_100 
            + 0.00793994182759050031*delta3*tau_inv165_100 - 0.0000779422690553850206*delta5*tau_inv65_100 
            + 0.0171119250297600001*tau_inv105_100*x1 + 0.15767003428866691*tau_inv165_100*tau_inv2_100 
            + 0.0163442433987670138*tau_inv99_100)*exp(delta2 + x0))*exp(-delta - delta2 - delta3))
