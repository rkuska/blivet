import parted
import six
import unittest

import blivet
from blivet.size import Size

if six.PY2:
    import mock
else:
    from unittest import mock

patch = mock.patch

class DiskLabelTestCase(unittest.TestCase):
    @patch("blivet.formats.disklabel.DiskLabel.freshPartedDisk", None)
    def testGetAlignment(self):
        dl = blivet.formats.disklabel.DiskLabel()
        dl._partedDisk = mock.Mock()
        dl._partedDevice = mock.Mock()
        dl._partedDevice.sectorSize = 512

        # 512 byte grain sze
        disklabel_alignment = parted.Alignment(grainSize=1, offset=0)
        dl._partedDisk.partitionAlignment = disklabel_alignment

        # 1 MiB grain size
        minimal_alignment = parted.Alignment(grainSize = 2048, offset=0)
        dl._partedDevice.minimumAlignment = minimal_alignment

        # 4 MiB grain size
        optimal_alignment = parted.Alignment(grainSize=8192, offset=0)
        dl._partedDevice.optimumAlignment = optimal_alignment

        # expected end alignments
        optimal_end_alignment = parted.Alignment(
                                        grainSize=optimal_alignment.grainSize,
                                        offset=-1)
        minimal_end_alignment = parted.Alignment(
                                        grainSize=minimal_alignment.grainSize,
                                        offset=-1)

        # make sure the private methods all return the expected values
        self.assertEqual(dl._getDiskLabelAlignment(), disklabel_alignment)
        self.assertEqual(dl._getMinimalAlignment(), minimal_alignment)
        self.assertEqual(dl._getOptimalAlignment(), optimal_alignment)

        # validate result when passing a start alignment to getEndAlignment
        self.assertEqual(dl.getEndAlignment(alignment=optimal_alignment),
                                            optimal_end_alignment)
        self.assertEqual(dl.getEndAlignment(alignment=minimal_alignment),
                         minimal_end_alignment)

        # by default we should return the optimal alignment
        self.assertEqual(dl.getAlignment(), optimal_alignment)
        self.assertEqual(dl.getEndAlignment(), optimal_end_alignment)

        # when passed a size smaller than the optimal io size we should return
        # the minimal alignment
        self.assertEqual(dl.getAlignment(size=Size("2 MiB")), minimal_alignment)
        self.assertEqual(dl.getEndAlignment(size=Size("2 MiB")),
                         minimal_end_alignment)

        # test the old deprecated properties' values
        self.assertEqual(dl.alignment, dl._getOptimalAlignment())
        self.assertEqual(dl.endAlignment, dl.getEndAlignment())
