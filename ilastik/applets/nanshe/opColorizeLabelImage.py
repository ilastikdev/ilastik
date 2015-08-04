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
__date__ = "$Oct 24, 2014 08:05:35 EDT$"



from lazyflow.graph import Operator, InputSlot, OutputSlot
from lazyflow.operators.opBlockedArrayCache import OpBlockedArrayCache

from ilastik.applets.base.applet import DatasetConstraintError

import itertools

import numpy
import matplotlib
import matplotlib.colors
import matplotlib.cm

import vigra

import nanshe
import nanshe.util.iters
import nanshe.imp.segment
import nanshe.util.xnumpy


class OpColorizeLabelImage(Operator):
    """
        Lazy computation of colors
    """
    name = "OpColorizeLabelImage"
    category = "Pointwise"


    Input = InputSlot()
    NumColors = InputSlot(value=256, stype='int')

    Output = OutputSlot()

    @staticmethod
    def colorTableList(num_colors):
        colors = []

        # Transparent for the zero label
        colors.append((0,0,0,0))

        rgb_color_values = list(nanshe.util.iters.splitting_xrange(num_colors))
        converter = matplotlib.colors.ColorConverter()

        for _ in rgb_color_values:
            a_rgb_color = tuple()
            for __ in converter.to_rgba(matplotlib.cm.gist_rainbow(_)):
                 a_rgb_color += ( int(round(255*__)), )

            colors.append(a_rgb_color)

        colors = numpy.asarray(colors, dtype=numpy.uint8)

        return(colors)

    def __init__(self, *args, **kwargs):
        super( OpColorizeLabelImage, self ).__init__( *args, **kwargs )

        self.colors = numpy.zeros((0,4), dtype=numpy.uint8)

        self.Input.notifyReady( self._checkConstraints )

    def _checkConstraints(self, *args):
        slot = self.Input

        sh = slot.meta.shape
        ndim = len(sh)
        ax = slot.meta.axistags
        tsh = slot.meta.getTaggedShape()

        if ("c" in tsh):
            if (tsh["c"] != 1):
                raise DatasetConstraintError(
                    "ColorizeLabelImage",
                    "Input image cannot have a non-singleton channel dimension.")
            if (ndim == 1):
                raise DatasetConstraintError(
                    "ColorizeLabelImage",
                    "There must be more dimensions than just the channel dimension.")
            if not ax[-1].isChannel():
                raise DatasetConstraintError(
                    "ColorizeLabelImage",
                    "Input image must have channel last." )

    def setupOutputs(self):
        # Copy the input metadata to both outputs
        self.Output.meta.assignFrom( self.Input.meta )
        self.Output.meta.shape = self.Output.meta.shape[:-1] + (4,)
        self.Output.meta.dtype = numpy.uint8

        dims = [_ for _ in self.Output.meta.axistags if not _.isChannel()]

        self.Output.meta.axistags = vigra.AxisTags(*(dims + [vigra.AxisInfo.c]))

    def execute(self, slot, subindex, roi, result):
        key = roi.toSlice()

        input_key = list(key)
        input_key = input_key[:-1] + [slice(None)]
        input_key = tuple(input_key)

        raw = self.Input[input_key].wait()

        if not self.colors.size:
            self.colors = OpColorizeLabelImage.colorTableList(self.NumColors.value)

        processed = numpy.empty(nanshe.util.iters.len_slices(key), dtype=numpy.uint8)
        for each_label in numpy.unique(raw):
            mask = (raw == each_label)
            mask = mask[..., 0]
            processed[mask, :] = self.colors[each_label, key[-1]]

        if slot.name == 'Output':
            result[...] = processed

    def propagateDirty(self, slot, subindex, roi):
        if (slot.name == "Input"):
            key = roi.toSlice()

            key = list(key)
            key = key[:-1] + [slice(None)]
            key = tuple(key)

            self.Output.setDirty(key)
        else:
            assert False, "Unknown dirty input slot"


class OpColorizeLabelImageCached(Operator):
    """
    Given an input image and max/min bounds,
    masks out (i.e. sets to zero) all pixels that fall outside the bounds.
    """
    name = "OpColorizeLabelImageCached"
    category = "Pointwise"


    Input = InputSlot()
    NumColors = InputSlot(value=256, stype='int')

    Output = OutputSlot()

    def __init__(self, *args, **kwargs):
        super( OpColorizeLabelImageCached, self ).__init__( *args, **kwargs )

        self.opColorizeLabelImage = OpColorizeLabelImage(parent=self)
        self.opColorizeLabelImage.NumColors.connect(self.NumColors)

        self.opCache = OpBlockedArrayCache(parent=self)
        self.opCache.fixAtCurrent.setValue(False)

        self.opColorizeLabelImage.Input.connect( self.Input )
        self.opCache.Input.connect( self.opColorizeLabelImage.Output )
        self.Output.connect( self.opCache.Output )

    def setupOutputs(self):
        axes_shape_iter = itertools.izip(self.opColorizeLabelImage.Output.meta.axistags,
                                         self.opColorizeLabelImage.Output.meta.shape)

        block_shape = []

        for each_axistag, each_len in axes_shape_iter:
            if each_axistag.isSpatial():
                each_len = min(each_len, 256)
            elif each_axistag.isTemporal():
                each_len = min(each_len, 50)

            block_shape.append(each_len)

        block_shape = tuple(block_shape)

        self.opCache.innerBlockShape.setValue(block_shape)
        self.opCache.outerBlockShape.setValue(block_shape)

    def setInSlot(self, slot, subindex, roi, value):
        pass

    def propagateDirty(self, slot, subindex, roi):
        pass
