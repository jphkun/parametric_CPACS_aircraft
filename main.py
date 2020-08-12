#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 08:15:57 2020

@author: Jean-Philippe Kuntzer

The objective of this program is to build a set number of aircrafts using the
CPACS file format.
    
    # TODO: add fuselage
    # TODO: add surface control
    # TODO: add winglets
    # TODO: add tail
    # TODO: add rudder
    # TODO: add spars/ribs/stringers

"""

# import Aircraft as Aircraft
import genNACA as naca
import numpy as np
import logging
import tigl3.configuration
from tixi3 import tixi3wrapper
from tigl3 import tigl3wrapper
from tigl3 import geometry
# from ctypes import *
# from genAircraft.__version__ import __version__

logging.basicConfig(level=logging.DEBUG)
__prog_name__ = 'gen_CPACS_Aircraft'
logger = logging.getLogger(__prog_name__+"."+__name__)

# def save(tixi_h, aircraft, filename):
#     aircraft.write_cpacs(aircraft.get_uid())
#     configAsString = tixi_h.exportDocumentAsString();
#     text_file = open(filename, "w")
#     text_file.write(configAsString)
#     text_file.close()


def cpacs_Structre(tixi_h,aircraft_name):
    # Now we insert a empty elements into the root element to create a
    # hierarchy of elements.

    path = ["/cpacs","/vehicles","/aircraft","/model","/reference","/point"]

    tixi_h.addTextElement("".join(path[:1]), "vehicles", 0)
    tixi_h.addTextElement("".join(path[:2]), "aircraft", 0)
    tixi_h.addTextElement("".join(path[:3]), "model", 0)
    tixi_h.addTextElement("".join(path[:3]), "description", 0)
    tixi_h.addTextAttribute("".join(path[:4]), "uID", aircraft_name)
    tixi_h.addTextElement("".join(path[:4]), "name", aircraft_name)
    tixi_h.addTextElement("".join(path[:4]), "description", "...")
    tixi_h.addTextElement("".join(path[:4]), "reference",0)
    tixi_h.addTextElement("".join(path[:5]), "area","10")
    tixi_h.addTextElement("".join(path[:5]), "length","1")
    tixi_h.addTextElement("".join(path[:5]), "point",0)
    tixi_h.addTextAttribute("".join(path[:6]), "uID", aircraft_name+"_point1")
    tixi_h.addPoint("".join(path[:6]), 0, 0, 0, "0.0")
    # Wing segment
    tixi_h.addTextElement("".join(path[:4]), "wings",0)
    # Fuselage segement
    tixi_h.addTextElement("".join(path[:4]), "fuselages",0)


def cpacs_Aircraft(tixi_h,naca_profile):
    # Computes profile and adds it to the CPACS file
    naca_airfoil = naca.Naca_airfoil(naca_profile, 250, False)
    naca_airfoil.NACAcompute()
    path = ["/cpacs","/vehicles","/profiles","/wingAirfoils","/wingAirfoil",
            "/pointList"]
    tixi_h.addTextElement("".join(path[:2]), "profiles", 0)
    tixi_h.addTextElement("".join(path[:3]), "wingAirfoils", 0)
    tixi_h.addTextElement("".join(path[:4]), "wingAirfoil", 0)
    tixi_h.addTextAttribute("".join(path[:5]),"uID",naca_profile)
    tixi_h.addTextElement("".join(path[:5]), "name", naca_profile)
    tixi_h.addTextElement("".join(path[:5]), "pointList", 0)
    tixi_h.addTextElement("".join(path[:6]), "x",
                          ''.join(['%.5f;' % num for num in naca_airfoil.x]))
    tixi_h.addTextElement("".join(path[:6]), "y",
                          ''.join(['%.5f;' % num for num in naca_airfoil.y]))
    tixi_h.addTextElement("".join(path[:6]), "z",
                          ''.join(['%.5f;' % num for num in naca_airfoil.z]))
    tixi_h.addTextAttribute("".join(path[:7])+"/x","mapType","vector")
    tixi_h.addTextAttribute("".join(path[:7])+"/y","mapType","vector")
    tixi_h.addTextAttribute("".join(path[:7])+"/z","mapType","vector")


def cpacs_save(aircraft,tixi_h,file_name):
    aircraft.write_cpacs(aircraft.get_uid())
    configAsString = tixi_h.exportDocumentAsString()
    text_file = open(file_name, "w")
    text_file.write(configAsString)
    text_file.close()


def fuselage_builder(aircraft):
    fuselages = aircraft.get_fuselages()
    # Creates new fuselage
    newFuselageUid = "fuselage_1"
    nFuselageSections = 4
    fuselages.create_fuselage(newFuselageUid, nFuselageSections,"fuselage_1ID")
    # TODO: The fuselages profiles need to be added to the CPACS before trying
    #       to desing the fuselage


def wing_builder1(span,
                  root_c,
                  tip_c,
                  sweep,
                  diheadral,
                  nWingSections,
                  name,
                  aircraft,
                  naca_profile,
                  cst2,
                  filename,
                  tixi_h):
    # Uploads instance for ease of use
    wings = aircraft.get_wings()
    # nWingSections = nWingSections+1

    # Creates new wing
    newWingUid = "Wing_1"
    wings.create_wing(newWingUid, nWingSections, naca_profile)
    wing = wings.get_wing(newWingUid)
    # Number of virtual subsections
    N = 10
    lineOg = np.linspace(0,span/2,nWingSections)
    lineMod = np.linspace(0,span/2,N*nWingSections)
    logger.debug("wing lineOg = \n"+str(lineOg))
    logger.debug("wing lineMod = \n"+str(lineMod))

    # Includes sweep to the points
    wing_Mod_clx = lineMod * np.sin(np.deg2rad(sweep))
    wing_Og_clx = lineOg * np.sin(np.deg2rad(sweep))
    wing_Mod_cly = lineMod * np.cos(np.deg2rad(sweep))
    wing_Og_cly = lineOg * np.cos(np.deg2rad(sweep))
    # Includes diheadral to the points
    wing_Mod_clz = lineMod * np.sin(np.deg2rad(diheadral))
    wing_Og_clz = lineOg * np.sin(np.deg2rad(diheadral))
    logger.debug("wing_Mod_clx = \n"+str(wing_Mod_clx))
    logger.debug("wing_Og_clx = \n"+str(wing_Og_clx))
    logger.debug("wing_Mod_cly = \n"+str(wing_Mod_cly))
    logger.debug("wing_Og_cly = \n"+str(wing_Og_cly))
    logger.debug("wing_Mod_clz = \n"+str(wing_Mod_clz))
    logger.debug("wing_Og_clz = \n"+str(wing_Og_clz))

    # how much chord length is changed for each point in the line
    delta_Mod_c = (root_c - tip_c)/np.max(lineMod)
    delta_Og_c = (root_c - tip_c)/np.max(lineOg)
    for i in range(0,wing.get_section_count()):
        logger.debug("i = "+str(i))
        # Position on the wing
        x1 = wing_Og_clx[i]
        y1 = wing_Og_cly[i]
        z1 = wing_Og_clz[i]

        logger.debug("x1 = "+str(x1))
        logger.debug("y1 = "+str(y1))
        logger.debug("z1 = "+str(z1))
    
        # x0 = wing_clx[index] # 0 et 9
        # y0 = wing_cly[index]
        # z0 = wing_clz[index]

        # Position derivatives
        if i == N:
            index = 10*(i-1)+9
        else:
            index = i
        dx1 = wing_Mod_clx[index] - wing_Mod_clx[index-1]
        dy1 = wing_Mod_cly[index] - wing_Mod_cly[index-1]
        dz1 = wing_Mod_clz[index] + cst2*wing_Mod_cly[index]**2 - \
              wing_Mod_clz[index-1]+cst2*wing_Mod_cly[index]**2

        # normal vector for quadratic deformation
        # dz2 = (z1 + cst2*y1**2) - (z0 + cst2*y0**2)

        # Wing scaling factor
        s_factor = root_c - delta_Og_c * lineOg[i]

        # Decompose section in workables items
        # if i == 0:
        #     sectionNumber = 1
        # else:
        #     sectionNumber = i+1
        segment = wing.get_section(i+1)
        element = segment.get_section_element(1)
        sec_el = element.get_ctigl_section_element()

        # Undeformed points
        centr = geometry.CTiglPoint(x1,y1,z1)
        normal_vec = geometry.CTiglPoint(0,-1,0)
        scale = geometry.CTiglPoint(s_factor,s_factor,s_factor)

        # Places the wing section
        element.set_scaling(scale)
        sec_el.set_center(centr)

        if i != 0:
            centr = geometry.CTiglPoint(x1, y1, z1 + cst2*y1**2)
            normal_vec = geometry.CTiglPoint(0,-dy1,-dz1)
            sec_el.set_center(centr)
            sec_el.set_normal(normal_vec)

    wing.set_symmetry(tigl3.core.TIGL_X_Z_PLANE)


def pointsWingType2():
    def f1(y0,y1,N,theta,alpha,chord0,chord1):
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
        nz = -np.ones(N) * np.sin(theta)
        
        # Computes new chord
        deltaC = (chord0 - chord1)/(y[-1]-y[0])
        chords = chord0 - deltaC*y
        return x,y,z,nx,ny,nz,chords

    def f2(y0,z0,r,theta,alpha,N,chord0,chord1):

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
        ny = np.sin(0.5*np.pi + deltaPhi + theta)
        nz = np.cos(0.5*np.pi + deltaPhi + theta)

        # Computes new chord
        deltaC = (chord0 - chord1)/(y[-1]-y[0])
        chords = chord0 - deltaC*(y-y[0])

        return x,y,z,nx,ny,nz,chords,yCenter,zCenter

    def f3(x0,y0,h,alpha,N,chord0,chord1):
        alpha = np.deg2rad(alpha)
        y = x0*np.ones(N)
        z = np.linspace(y0,y0+h,N)
        x = -y*np.sin(alpha)
        nx = np.zeros(N)
        ny = np.zeros(N)
        nz = np.ones(N)
        
        # Computes new chord
        deltaC = (chord0 - chord1)/(z[-1] - z[0])
        chords = chord0 - deltaC*(z-z[0])
        
        return x,y,z,nx,ny,nz,chords

    # Computes the points
    y0 = 0
    y1 = 0.5
    N1 = 2
    N2 = 5
    N3 = 2
    theta = 0
    alpha = 0
    x1,y1,z1,nx1,ny1,nz1,chrods1 = f1(y0,y1,N1,theta,alpha,0.2,0.2)
    # x2,y2,z2,nx2,ny2,nz2,chrods2,cy,cz = f2(y1[-1],z1[-1],0.02,theta,alpha,N2,0.15,0.08)
    # x3,y3,z3,nx3,ny3,nz3,chrods3 = f3(y2[-1],z2[-1],0.02,alpha,N3,0.08,0.07)

    # x = np.concatenate((x1, x2[1:], x3[1:]))
    # y = np.concatenate((y1, y2[1:], y3[1:]))
    # z = np.concatenate((z1, z2[1:], z3[1:]))
    x = x1
    y = y1
    z = z1

    # nx = np.concatenate((nx1, nx2[1:], nx3[1:]))
    # ny = np.concatenate((ny1, ny2[1:], ny3[1:]))
    # nz = np.concatenate((nz1, nz2[1:], nz3[1:]))
    nx = nx1
    ny = ny1
    nz = nz1

    # chords = np.concatenate((chrods1, chrods2[1:], chrods3[1:]))
    chords = chrods1
    print(chords)
    return x,y,z,nx,ny,nz,chords

def wing_builder2(x,y,z,nx,ny,nz,chords,name,aircraft,naca_profiles,filename,tixi_h):
    
    # TODO add wings profile
    
    # Uploads instance for ease of use
    wings = aircraft.get_wings()
    # nWingSections = nWingSections+1

    # Creates new wing
    newWingUid = "Wing_1"
    nWingSections = len(x)
    wings.create_wing(newWingUid, nWingSections, naca_profiles)
    
    wing = wings.get_wing(newWingUid)

    for i in range(0,wing.get_section_count()):
        logger.debug("i = "+str(i))

        # Wing scaling factor
        deltaChord = chords[0] - chords[i]
        s_factor = chords[0] - deltaChord

        # Decompose section in workables items
        # if i == 0:
        #     sectionNumber = 1
        # else:
        #     sectionNumber = i+1
        segment = wing.get_section(i+1)
        element = segment.get_section_element(1)
        sec_el = element.get_ctigl_section_element()

        # Undeformed points
        centr = geometry.CTiglPoint(x[i]+0*deltaChord,y[i],z[i])
        normal_vec = geometry.CTiglPoint(nx[i],ny[i],nz[i])
        scale = geometry.CTiglPoint(s_factor,s_factor,s_factor)

        # Places the wing section
        element.set_scaling(scale)
        sec_el.set_center(centr)

        if i != 0:
            centr = geometry.CTiglPoint(x[i]+0.5*deltaChord,y[i],z[i])
            normal_vec = geometry.CTiglPoint(nx[i],-ny[i],nz[i])
            sec_el.set_center(centr)
            sec_el.set_normal(normal_vec)

    wing.set_symmetry(tigl3.core.TIGL_X_Z_PLANE)

def main():
    names = ["straightWing"]

    logger.info("Program started")

    # Aircraft variables
    # [m] Wing span
    span = 1.0
    # [-] sweep angle in degrees. aft if negative
    sweep = 0
    # [-] diheadral angle in degree - anhedral if negative
    diheadral = 5
    # [m] root chord
    root_c = 0.22
    # [m] tip chord
    tip_c = 0.15
    # Airfoil profile
    naca_profile = "NACA 4422"
    # Number of wing sections
    nWingSections = 2

    # CPACS variables
    aircraft_name = "FlyingWing"
    creator = "Jean-Philippe Kuntzer"
    version = "1"
    description = "Test for aeroelatic deformation"
    cpacsVersion = "3.0"
    for i in range(len(names)):
        # Tigl and Tixi handles
        tixi_h = tixi3wrapper.Tixi3()
        tigl_h = tigl3wrapper.Tigl3()

        # Create a new document for writing with root element named
        # "plane". A file name is attributed to this document on saving.
        CPACS_name = "cpacs"
        tixi_h.create(CPACS_name)

        # First a header containing the tool name and version and the author
        # of the file is added. A timestamp is added automatically, as well.
        tixi_h.addCpacsHeader(aircraft_name,
                              creator,
                              version,
                              description,
                              cpacsVersion)

        # defines a CPACS structres and give the miinum setup
        cpacs_Structre(tixi_h,aircraft_name)
        cpacs_Aircraft(tixi_h,naca_profile)

        # Links tixi handler to CPACS files
        tigl_h.open(tixi_h,aircraft_name)

        # Uploads tixi handel information into tigl information
        mgr = tigl3.configuration.CCPACSConfigurationManager_get_instance()
        aircraft = mgr.get_configuration(tigl_h._handle.value)
        # cst2 = np.linspace(0,0.5,len(names))
        cst2 = [0.0]
        # cst2 = 0.5*np.ones(len(names)) # np.linspace(0,0.5,len(names))
        filename = names[i] + ".xml"
        # wing_builder(span,
        #              root_c,
        #              tip_c,
        #              sweep,
        #              diheadral,
        #              nWingSections,
        #              names[i],
        #              aircraft,
        #              naca_profile,
        #              cst2[i],
        #              filename,tixi_h)
        # # fuselage_builder(aircraft)
        # cpacs_save(aircraft,tixi_h,filename)
        x,y,z,nx,ny,nz,chords = pointsWingType2()
        # chords = 0.2*(1-y)*np.ones(len(x))
        wing_builder2(x,y,z,nx,ny,nz,chords,names,aircraft,naca_profile,filename,tixi_h)
        cpacs_save(aircraft,tixi_h,filename)
    logger.debug("Program ended")


if __name__ == "__main__":
    main()
