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
from ilastik.workflow import Workflow

from lazyflow.graph import Graph

from ilastik.applets.dataSelection import DataSelectionApplet
from ilastik.applets.labeling import LabelingApplet
from ilastik.applets.labeling import LabelingSingleLaneApplet

class LabelingWorkflow(Workflow):
    def __init__( self, shell, headless, workflow_cmdline_args, project_creation_args, *args, **kwargs):
        # Create a graph to be shared by all operators
        graph = Graph()
        super(LabelingWorkflow, self).__init__( shell, headless, workflow_cmdline_args, project_creation_args, graph=graph, *args, **kwargs )
        self._applets = []

        # Create applets
        self.dataSelectionApplet = DataSelectionApplet(self, "Input Data", "Input Data", supportIlastik05Import=True, batchDataGui=False)
        self.labelingSingleLaneApplet = LabelingSingleLaneApplet(self, "Generic Labeling (single-lane)")
        self.labelingMultiLaneApplet = LabelingApplet(self, "Generic Labeling (multi-lane)")

        opDataSelection = self.dataSelectionApplet.topLevelOperator
        opDataSelection.DatasetRoles.setValue( ["Raw Data"] )

        self._applets.append( self.dataSelectionApplet )
        self._applets.append( self.labelingSingleLaneApplet )
        self._applets.append( self.labelingMultiLaneApplet )

    def connectLane(self, laneIndex):
        opDataSelection = self.dataSelectionApplet.topLevelOperator.getLane(laneIndex)
        opSingleLaneLabeling = self.labelingSingleLaneApplet.topLevelOperator.getLane(laneIndex)
        opMultiLabeling = self.labelingMultiLaneApplet.topLevelOperator.getLane(laneIndex)
        
        # Connect top-level operators
        opSingleLaneLabeling.InputImage.connect( opDataSelection.Image )
        opSingleLaneLabeling.LabelsAllowedFlag.connect( opDataSelection.AllowLabels )

        opMultiLabeling.InputImages.connect( opDataSelection.Image )
        opMultiLabeling.LabelsAllowedFlags.connect( opDataSelection.AllowLabels )

    @property
    def applets(self):
        return self._applets

    @property
    def imageNameListSlot(self):
        return self.dataSelectionApplet.topLevelOperator.ImageName
