#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 08:21:58 2020

@author: cfse2
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
logger = logging.getLogger(__name__)


class Naca_airfoil:
    def __init__(self,naca_name,N,plt=True):
        """
        Initializes the NACA airfoil

        Parameters
        ----------
        naca_name : TYPE
            DESCRIPTION.
        N : TYPE
            DESCRIPTION.
        plt : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        # Name of the airfoil
        self.name = naca_name
        # Number of points
        self.N = N/2
        # [m] Points of the airfoil (_u: upper, _l: lower)
        self.xu = np.linspace(0,1,N)
        self.xl = np.linspace(0,1,N)
        self.x = np.concatenate((self.xu, np.flip(self.xl)))
        self.yu = np.empty((N))
        self.yl = np.empty((N))
        self.ytu = np.empty((N))
        self.ytl = np.empty((N))
        self.z = np.concatenate((self.yu, np.flip(self.yl)))
        self.y = np.zeros((2*N))
        self.dyc = np.zeros((N))
        # Camber line y position (_u: upper, _l: lower)
        self.yc = np.zeros((N))
        # [m] Chord length
        self.c = 1
        # Macximum camber in chord length
        self.m = 0.01*int(naca_name[-4:-3])
        # Distance of the maximum camber from the leading edge
        self.p = 0.1*int(naca_name[-3:-2])
        # Thickness of the airfoil
        self.t = 0.01*int(naca_name[-2:])
        # Leading edge radius
        self.r = 1.019*self.t**2 / self.c
        # Plotting variable
        self.plot = plt

    def NacaCamber(self):
        """
        Computes the camber line and its derivative
        """
        c = self.c
        m = self.m
        p = self.p
        x = self.xu

        for i in range(len(self.xu)):
            if x[i] <= self.p*self.c:
                # Camber line
                self.yc[i] = (m/p**2) * (2*p*x[i] - x[i]**2)
                # Camber line derivative
                self.dyc[i] = (2*m/p**2) * (p-x[i])
            else:
                # Camber line
                self.yc[i] = (m/(1-p)**2) * ((1-2*p) + 2*p*x[i] - x[i]**2)
                # Camber line derivative
                self.dyc[i] = (2*m/(1-p)**2) * (p-x[i])

    def NacaEquation(self,x,t):
        """
        Computes the upper and lower surface of a symmetric NACA airfoil. This
        function is also used for the computation of a NACA cambered airfoil.

        Parameters
        ----------
        x : TYPE
            "x" position of the airfoil point to compute
        t : TYPE
            Airfoil thickness

        Returns
        -------
        y_t : TYPE
            "y" position of the airfoil

        """
        a0 = 0.2969
        a1 = 0.1260
        a2 = 0.3516
        a3 = 0.2843
        a4 = 0.1036

        y_t = 5*t * (a0*x**0.5 - a1*x - a2*x**2 + a3*x**3 - a4*x**4)

        return y_t

    def NACA4digitsSym(self):
        """
        Computes the points for a symmetric 4 digits NACA airfoil
        """
        self.ytu =  self.NacaEquation(self.xu,self.t)
        self.ytl = -self.NacaEquation(self.xl,self.t)
        # Done for estitic reasons
        self.yu = self.ytu 
        self.yl = self.ytl
        self.z = np.concatenate((self.yu, np.flip(self.yl)))
        if self.plot:
            plt.figure(self.name)
            plt.title(self.name)
            plt.plot(self.xu,self.yu)
            plt.plot(self.xl,self.yl)
            plt.axis('equal')

    def NACA4digitsCam(self):
        """
        Computes the points for a cambered 4 digits NACA airfoil
        """
        self.ytu = self.NacaEquation(self.xu,self.t)
        self.ytl = self.NacaEquation(self.xl,self.t)
        self.NacaCamber()
        teta = np.arctan(self.dyc)
        self.xu = self.xu - self.ytu * np.sin(teta)
        self.xl = self.xl + self.ytl * np.sin(teta)
        self.yu = self.yc + self.ytu * np.cos(teta)
        self.yl = self.yc - self.ytl * np.cos(teta)
        self.z = np.concatenate((self.yu, np.flip(self.yl)))

        if self.plot:
            plt.figure(self.name)
            plt.title(self.name)
            plt.plot(self.xu,self.yu,color="b")
            plt.plot(self.xl,self.yl,color="b")
            plt.plot(self.xl,self.yc,color="r")
            plt.axis('equal')

    def NACAcompute(self):
        """
        Selects which NACA type it is
        TODO: Add a try - except
        """
        if self.p == 0:
            self.NACA4digitsSym()
        else:
            self.NACA4digitsCam()
