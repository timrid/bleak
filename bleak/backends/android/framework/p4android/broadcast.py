from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:

    class BroadcastReceiver:
        def __init__(
            self,
            callback: Callable[[Any, Any], None],
            actions: list[str] | None = None,
            categories: list[str] | None = None,
        ): ...

        def start(self): ...

        def stop(self): ...
else:
    from android.broadcast import BroadcastReceiver  # type: ignore
