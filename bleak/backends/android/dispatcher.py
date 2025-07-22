import asyncio
import dataclasses
import logging
import sys
import warnings
from typing import Any, Callable, Generic, TypeVar, overload

if sys.version_info < (3, 12):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from bleak.exc import BleakError

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclasses.dataclass
class CallbackResult:
    pass


@dataclasses.dataclass
class EmptyCallbackResult(CallbackResult):
    pass


CallbackResultT = TypeVar("CallbackResultT", bound=CallbackResult)


@dataclasses.dataclass(frozen=True)
class CallbackApi(Generic[CallbackResultT]):
    pass


@dataclasses.dataclass
class CallbackState:
    failure_str: str | None
    callback_result: CallbackResult


P = ParamSpec("P")
R = TypeVar("R")


def dispatch_func(
    func: Callable[P, R], /, *args: P.args, **kwargs: P.kwargs
) -> Callable[[], R]:
    def newfunc():
        return func(*args, **kwargs)

    return newfunc


class CallbackDispatcher:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self.states: dict[CallbackApi, CallbackState] = {}
        self.futures: dict[CallbackApi, asyncio.Future] = {}

    @overload
    async def perform_and_wait(
        self,
        dispatch_api: Callable[[], bool],
        callback_api: CallbackApi[CallbackResultT],
        callback_expected_result: CallbackResultT | None = ...,
        unless_already: bool = False,
        dispatch_result_indicates_status: bool = True,
    ) -> CallbackResultT: ...
    @overload
    async def perform_and_wait(
        self,
        dispatch_api: Callable[[], T],
        callback_api: CallbackApi[CallbackResultT],
        callback_expected_result: CallbackResultT | None = None,
        unless_already: bool = False,
        dispatch_result_indicates_status: bool = False,
    ) -> tuple[T, CallbackResultT]: ...
    async def perform_and_wait(
        self,
        dispatch_api: Callable[[], T],
        callback_api: CallbackApi[CallbackResultT],
        callback_expected_result: CallbackResultT | None = None,
        unless_already: bool = False,
        dispatch_result_indicates_status: bool = True,
    ) -> Any:
        """
        Perform an API call and wait for the result.

        :param dispatch_api:
                The API function to call, that triggers the callback.
        :param callback_api:
                The callback to wait for to get the result.
        :param callback_expected_result:
                The expected result from the callback.
        :param unless_already:
                If True, do not wait if the result is already in states.
        :param dispatch_result_indicates_status:
                If True, the return will be the callback result,
                otherwise it will be a tuple of (dispatch api result, callback result).

        :return:
                If dispatch_result_indicates_status=True: callback result
                If dispatch_result_indicates_status=False: tuple of (dispatch api result, callback result)
        """
        callback_result = None
        if unless_already:
            if callback_api in self.states:
                callback_result = self.states[callback_api].callback_result

        if callback_result is not None:
            logger.debug(
                f"Not waiting for android api {callback_api} because found {callback_expected_result}"
            )
            dispatch_result = True
        else:
            logger.debug(f"Waiting for android api {callback_api}")

            # Create a future, that is filled from the callback
            state: asyncio.Future[CallbackResult] = self._loop.create_future()
            self.futures[callback_api] = state

            # Call the API function, which will trigger the callback to fill the future
            dispatch_result = dispatch_api()
            if dispatch_result_indicates_status and not dispatch_result:
                del self.futures[callback_api]
                raise BleakError(f"api call failed, not waiting for {callback_api}")

            # Wait for the future to be filled by the callback
            callback_result = await state
            if callback_result is None:
                raise BleakError(
                    "Expected", callback_expected_result, "got", callback_result
                )

            logger.debug(f"{callback_api} succeeded {callback_result}")

        if dispatch_result_indicates_status:
            return callback_result
        else:
            return (dispatch_result, callback_result)

    def result_state_threadsafe(
        self,
        failure_str: str | None,
        callback_api: CallbackApi[CallbackResultT],
        callback_result: CallbackResultT,
    ):
        self._loop.call_soon_threadsafe(
            self._result_state_unthreadsafe, failure_str, callback_api, callback_result
        )

    def _result_state_unthreadsafe(
        self,
        failure_str: str | None,
        callback_api: CallbackApi[CallbackResultT],
        callback_result: CallbackResultT,
    ):
        logger.debug(
            f"Java state transfer {callback_api} error={failure_str} callback_result={callback_result}"
        )
        self.states[callback_api] = CallbackState(failure_str, callback_result)
        future = self.futures.get(callback_api, None)
        if future is not None and not future.done():
            if failure_str is None:
                future.set_result(callback_result)
            else:
                future.set_exception(
                    BleakError(callback_api, failure_str, callback_result)
                )
        else:
            if failure_str is not None:
                # an error happened with nothing waiting for it
                exception = BleakError(callback_api, failure_str, callback_result)
                namedfutures = [
                    namedfuture
                    for namedfuture in self.futures.items()
                    if not namedfuture[1].done()
                ]
                if len(namedfutures):
                    # send it on existing requests
                    for name, future in namedfutures:
                        warnings.warn(f"Redirecting error without home to {name}")
                        future.set_exception(exception)
                else:
                    # send it on the event thread
                    raise exception
