#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 13:13:27 2020

@author: cfse2
"""

import numpy as np
import matplotlib.pyplot as plt

def f1(y0,y1,N,theta,alpha):
    """
    Computes the first part of the wing
    """
    # General variables set up
    theta = np.deg2rad(theta)
    alpha = np.deg2rad(alpha)
    m = np.tan(theta)
    h = 0

    # Computes point
    y = np.linspace(y0,y1,N)
    x = -y*np.sin(alpha)
    z = m*y + h

    # desired normal vector
    nx = np.zeros(N)
    ny = np.ones(N) * np.cos(theta)
    nz = np.ones(N) * np.sin(theta)
    
    
    return x,y,z,nx,ny,nz

def f2(y0,z0,r,theta,alpha,N):

    # Sets up the general variables
    theta = np.deg2rad(theta)
    alpha = np.deg2rad(alpha)
    phi = 0.5*np.pi - theta
    r = r/np.cos(r)
    N += 1
    # Finds the center of the circle
    yCenter = y0 - r*np.cos(phi)
    zCenter = z0 + r*np.sin(phi)

    # Computes the new points
    deltaPhi = phi/(N-1)*np.arange(0,N)
    y = yCenter + r*np.cos(1.5*np.pi + deltaPhi + theta)
    z = zCenter + r*np.sin(1.5*np.pi + deltaPhi + theta)
    x = -y*np.sin(alpha)

    # Computes the new normal vector
    nx = np.zeros(N)
    ny = np.cos(0*np.pi + deltaPhi + theta)
    nz = np.sin(0*np.pi + deltaPhi + theta)
    return x,y,z,nx,ny,nz,yCenter,zCenter

def f3(x0,y0,h,alpha,N):
    alpha = np.deg2rad(alpha)
    y = x0*np.ones(N)
    z = np.linspace(y0,y0+h,N)
    x = -y*np.sin(alpha)
    nx = np.zeros(N)
    ny = np.zeros(N)
    nz = np.ones(N)
    return x,y,z,nx,ny,nz

# Computes the points
y0 = 0
y1 = 0.5
N1 = 2
N2 = 20
N3 = 2
theta = 5
alpha = 10
x1,y1,z1,nx1,ny1,nz1 = f1(y0,y1,N1,theta,alpha)
x2,y2,z2,nx2,ny2,nz2,cy,cz = f2(y1[-1],z1[-1],0.05,theta,alpha,N2)
x3,y3,z3,nx3,ny3,nz3 = f3(y2[-1],z2[-1],0.05,alpha,N3)

x = np.concatenate((x1, x2[1:], x3[1:]))
y = np.concatenate((y1, y2[1:], y3[1:]))
z = np.concatenate((z1, z2[1:], z3[1:]))

nx = np.concatenate((nx1, nx2[1:], nx3[1:]))
ny = np.concatenate((ny1, ny2[1:], ny3[1:]))
nz = np.concatenate((nz1, nz2[1:], nz3[1:]))

# # second part
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# ax.plot(x1, y1, z1, label='parametric curve')
# ax.plot(x2, y2, z2, label='parametric curve')
# ax.plot(x3, y3, z3, label='parametric curve')
# ax.quiver(x1,y1,z1,0.1*nx1,0.1*ny1,0.1*nz1)
# ax.quiver(x2,y2,z2,0.1*nx2,0.1*ny2,0.1*nz2)
# ax.quiver(x3,y3,z3,0.1*nx3,0.1*ny3,0.1*nz3)
# ax.legend()

# var1 = -0.5
# var2 = 0.5
# ax.set_xlim(0,-var2)
# ax.set_ylim(0,var2)
# ax.set_zlim(0,var2)

# plt.show()


# # Plots figure
# plt.figure("Wing")
# plt.plot(y1, z1)
# plt.plot(cy, cz,"o")
# plt.plot(y2, z2)
# plt.plot(y3, z3)
# plt.xlim(0,0.6)
# plt.ylim(0,0.6)
# plt.axis('equal')
# plt.show()