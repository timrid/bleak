
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.service.assist
import android.service.autofill
import android.service.carrier
import android.service.chooser
import android.service.controls
import android.service.credentials
import android.service.dreams
import android.service.media
import android.service.notification
import android.service.persistentdata
import android.service.quickaccesswallet
import android.service.quicksettings
import android.service.restrictions
import android.service.textservice
import android.service.voice
import android.service.vr
import android.service.wallpaper
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.service")``.

    assist: android.service.assist.__module_protocol__
    autofill: android.service.autofill.__module_protocol__
    carrier: android.service.carrier.__module_protocol__
    chooser: android.service.chooser.__module_protocol__
    controls: android.service.controls.__module_protocol__
    credentials: android.service.credentials.__module_protocol__
    dreams: android.service.dreams.__module_protocol__
    media: android.service.media.__module_protocol__
    notification: android.service.notification.__module_protocol__
    persistentdata: android.service.persistentdata.__module_protocol__
    quickaccesswallet: android.service.quickaccesswallet.__module_protocol__
    quicksettings: android.service.quicksettings.__module_protocol__
    restrictions: android.service.restrictions.__module_protocol__
    textservice: android.service.textservice.__module_protocol__
    voice: android.service.voice.__module_protocol__
    vr: android.service.vr.__module_protocol__
    wallpaper: android.service.wallpaper.__module_protocol__
