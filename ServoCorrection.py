#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 11:39:24 2019

@author: pz513
"""
import math as m

trimR=1442
trimP=1461
R=float(1500-trimR)/500*70#/180*m.pi
P=float(1500-trimP)/500*70#/180*m.pi

S2=pow(3.0,-0.5)*(1.0/m.tan(R)-1.0/m.tan(P))
S1=-pow(3.0,-0.5)*(1.0/m.tan(R)+1.0/m.tan(P))