"""
Basic example based test for the stm reader
"""

import os
from glob import glob
from pathlib import Path

from pynxtools.testing.nexus_conversion import ReaderTest


def test_nexus_conversion(caplog, tmp_path):
    """
    Tests the conversion into nexus.
    """
    caplog.clear()
    dir_path = Path(__file__).parent / "data"
    test = ReaderTest(
        nxdl="NXraman",
        reader_name="raman",
        files_or_dir=glob(os.path.join(dir_path, "*")),
        tmp_path=tmp_path,
        caplog=caplog,
    )
    test.convert_to_nexus(caplog_level="WARNING", ignore_undocumented=False)
    test.check_reproducibility_of_nexus()
