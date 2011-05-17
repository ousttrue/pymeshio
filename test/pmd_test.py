import pymeshio.pmd
import sys

PMD_FILE="K:/MMD/model/official/miku.pmd"

def test_pmd_load():
    io=pymeshio.pmd.IO()
    assert io.read(PMD_FILE)

