
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import typing



class PersistentDataBlockManager:
    def isFactoryResetProtectionActive(self) -> bool: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.service.persistentdata")``.

    PersistentDataBlockManager: typing.Type[PersistentDataBlockManager]
