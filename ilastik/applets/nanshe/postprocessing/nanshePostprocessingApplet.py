###############################################################################
#   ilastik: interactive learning and segmentation toolkit
#
#       Copyright (C) 2011-2014, the ilastik developers
#                                <team@ilastik.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# In addition, as a special exception, the copyright holders of
# ilastik give you permission to combine ilastik with applets,
# workflows and plugins which are not covered under the GNU
# General Public License.
#
# See the LICENSE file for details. License information is also available
# on the ilastik web site at:
#		   http://ilastik.org/license.html
###############################################################################

__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Oct 23, 2014 16:26:21 EDT$"



from ilastik.applets.base.standardApplet import StandardApplet

from opNanshePostprocessing import OpNanshePostprocessing
from ilastik.applets.nanshe.postprocessing.nanshePostprocessingSerializer import NanshePostprocessingSerializer

class NanshePostprocessingApplet( StandardApplet ):
    """
    This is a simple thresholding applet
    """
    def __init__( self, workflow, guiName, projectFileGroupName ):
        super(NanshePostprocessingApplet, self).__init__(guiName, workflow)
        self._serializableItems = [ NanshePostprocessingSerializer(self.topLevelOperator, projectFileGroupName) ]

    @property
    def singleLaneOperatorClass(self):
        return OpNanshePostprocessing

    @property
    def broadcastingSlots(self):
        return ["SignificanceThreshold", "WaveletTransformScale", "NoiseThreshold",\
                "AcceptedRegionShapeConstraints_MajorAxisLength_Min",\
                "AcceptedRegionShapeConstraints_MajorAxisLength_Min_Enabled",\
                "AcceptedRegionShapeConstraints_MajorAxisLength_Max",\
                "AcceptedRegionShapeConstraints_MajorAxisLength_Max_Enabled",\
                "PercentagePixelsBelowMax", "MinLocalMaxDistance",\
                "AcceptedNeuronShapeConstraints_Area_Min",\
                "AcceptedNeuronShapeConstraints_Area_Min_Enabled",\
                "AcceptedNeuronShapeConstraints_Area_Max",\
                "AcceptedNeuronShapeConstraints_Area_Max_Enabled",\
                "AcceptedNeuronShapeConstraints_Eccentricity_Min",\
                "AcceptedNeuronShapeConstraints_Eccentricity_Min_Enabled",\
                "AcceptedNeuronShapeConstraints_Eccentricity_Max",\
                "AcceptedNeuronShapeConstraints_Eccentricity_Max_Enabled",\
                "AlignmentMinThreshold", "OverlapMinThreshold", "Fuse_FractionMeanNeuronMaxThreshold"]


    @property
    def singleLaneGuiClass(self):
        from ilastik.applets.nanshe.postprocessing.nanshePostprocessingGui import NanshePostprocessingGui
        return NanshePostprocessingGui

    @property
    def dataSerializers(self):
        return self._serializableItems
