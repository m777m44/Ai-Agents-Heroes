#!/usr/bin/env python3
"""Writes BuildStamp.java so the running APK can always be identified in the UI."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
import datetime
stamp = "b" + datetime.datetime.now().strftime("%y%m%d-%H%M")
src = '''package com.raf3ly.app;

/** Generated at build time - shown in the welcome card and in About. */
public final class BuildStamp {
    public static final String VALUE = "%s";

    private BuildStamp() {
    }
}
''' % stamp
open(_ROOT + "/app/src/java/com/raf3ly/app/BuildStamp.java", "w", encoding="utf-8").write(src)
print("build stamp", stamp)
