#!/usr/bin/python
# coding: utf-8
"""
utitlities for pmd and vmd loading. 

- python2 and python3 compatibility.

"""
import sys
import os.path


"""
utility functions for python2 and python3 compatibility.
"""
if sys.version_info[0]>=3:
    xrange=range

if sys.version_info[0]<3:
    def truncate_zero(src):
        """
        drop after 0x00
        """
        assert(type(src)==bytes)
        pos = src.find(b"\x00")
        if pos >= 0:
            return src[:pos]
        else:
            return src
else:
    def truncate_zero(src):
        """
        drop after 0x00
        """
        assert(type(src)==bytes)
        pos = src.find(b"\x00")
        if pos >= 0:
            return src[:pos].decode('cp932')
        else:
            return src.decode('cp932')


if sys.version_info[0]<3:
    def to_str(src):
        """
        str or unicode to str
        """
        t=type(src)
        if t==unicode:
            return src.encode('cp932')
        elif t==str:
            return src
        else:
            raise "INVALID str: %s" % t

    def from_str(src):
        """
        do nothing
        """
        return src

else:
    def to_str(src):
        """
        bytes or str to str
        """
        t=type(src)
        if t==str:
            return src
        elif t==bytes:
            return src.decode('cp932')
        else:
            raise "INVALID str: %s" % t

    def from_str(src):
        """
        str to bytes
        """
        return src.encode('cp932')


