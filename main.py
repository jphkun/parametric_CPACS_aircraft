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

def wing_builder(span,
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
    # fuselages = aircraft.get_fuselages()

    # Creates new wing
    newWingUid = "Wing_1"
    wings.create_wing(newWingUid, nWingSections, naca_profile)
    wing = wings.get_wing(newWingUid)
    line = np.linspace(0,span/2,10*nWingSections)
    wing_clx = np.zeros(10*nWingSections)
    wing_cly = np.zeros(10*nWingSections)
    wing_clz = np.zeros(10*nWingSections)

    # Includes sweep to the points
    wing_clx = line * np.sin(np.deg2rad(sweep))
    wing_cly = line * np.cos(np.deg2rad(sweep))

    # Includes diheadral to the points
    wing_clz = line * np.sin(np.deg2rad(diheadral))
    delta_c = (root_c - tip_c)/np.max(line)

    for i in range(1,wing.get_section_count()+1):
        # Position on the wing
        x1 = wing_clx[10*(i-1)]
        y1 = wing_cly[10*(i-1)]
        z1 = wing_clz[10*(i-1)]
        x0 = wing_clx[10*(i-1)-1]
        y0 = wing_cly[10*(i-1)-1]
        z0 = wing_clz[10*(i-1)-1]

        # Position derivatives
        dx1 = x1 - x0
        dy1 = y1 - y0
        dz1 = z1 - z0

        # normal vector for quadratic deformation
        dz2 = (z1 + cst2*y1**2) - (z0 + cst2*y0**2)

        # Wing scaling factor
        s_factor = root_c - delta_c * line[10*(i-1)]

        # Decompose section in workables items
        segment = wing.get_section(i)
        element = segment.get_section_element(1)
        sec_el = element.get_ctigl_section_element()

        # Undeformed points
        centr = geometry.CTiglPoint(x1,y1,z1)
        normal_vec = geometry.CTiglPoint(0,-1,0)
        scale = geometry.CTiglPoint(s_factor,s_factor,s_factor)

        # Places the wing section
        element.set_scaling(scale)
        sec_el.set_center(centr)

        if i != 1:
            centr = geometry.CTiglPoint(x1, y1, z1 + cst2*y1**2)
            normal_vec = geometry.CTiglPoint(0,-dy1,-dz2)
            sec_el.set_center(centr)
            sec_el.set_normal(normal_vec)

    wing.set_symmetry(tigl3.core.TIGL_X_Z_PLANE)


def main():
    names = ["01_EbeeX","02_EbeeX","03_EbeeX","04_EbeeX","05_EbeeX"]

    logger.info("Program started")

    # Aircraft variables
    # [m] Wing span
    span = 1.1
    # [-] sweep angle in degrees. aft if negative
    sweep = 30
    # [-] diheadral angle in degree - anhedral if negative
    diheadral = 10
    # [m] root chord
    root_c = 0.3
    # [m] tip chord
    tip_c = 0.2
    # Airfoil profile
    naca_profile = "NACA 2218"
    # Number of wing sections
    nWingSections = 10

    # CPACS variables
    aircraft_name = "EbeeX"
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
        cst2 = 0.5*np.ones(len(names)) # np.linspace(0,0.5,len(names))

        filename = names[i] + ".xml"
        wing_builder(span,
                     root_c,
                     tip_c,
                     sweep,
                     diheadral,
                     nWingSections,
                     names[i],
                     aircraft,
                     naca_profile,
                     cst2[i],
                     filename,tixi_h)
        # fuselage_builder(aircraft)
        cpacs_save(aircraft,tixi_h,filename)
    logger.debug("Program ended")


if __name__ == "__main__":
    main()
