
import sys

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import typing

import java.applet
import java.awt
import java.beans
import java.io
import java.lang
import java.math
import java.net
import java.nio
import java.rmi
import java.security
import java.sql
import java.text
import java.time
import java.util

class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("java")``.

    applet: java.applet.__module_protocol__
    awt: java.awt.__module_protocol__
    beans: java.beans.__module_protocol__
    io: java.io.__module_protocol__
    lang: java.lang.__module_protocol__
    math: java.math.__module_protocol__
    net: java.net.__module_protocol__
    nio: java.nio.__module_protocol__
    rmi: java.rmi.__module_protocol__
    security: java.security.__module_protocol__
    sql: java.sql.__module_protocol__
    text: java.text.__module_protocol__
    time: java.time.__module_protocol__
    util: java.util.__module_protocol__

class jboolean:
    def __init(self, value):
        ...

class jbyte:
    def __init(self, value, truncate=False):
        ...

class jshort:
    def __init(self, value, truncate=False):
        ...

class jint:
    def __init(self, value, truncate=False):
        ...

    def __int__(self):
        ...

class jlong:
    def __init(self, value, truncate=False):
        ...

class jfloat:
    def __init(self, value, truncate=False):
        ...

class jdouble:
    def __init(self, value, truncate=False):
        ...

class jchar:
    def __init(self, value):
        ...

class jvoid:
    ...

class jclass:
    def __init(self, cls_name):
        ...

class jarray:
    def __init__(self, element_type):
        ...

def cast(cls, obj):
    ...

def set_import_enabled(enable):
    ...

def dynamic_proxy(*implements):
    ...

def static_proxy(extends=None, *implements, package=None, modifiers='public'):
    ...

def method(return_type, arg_types, *, modifiers='public', throws=None):
    ...

def Override(return_type, arg_types, *, modifiers='public', throws=None):
    ...

def constructor(arg_types, *, modifiers='public', throws=None):
    ...

def detach():
    ...