import functools
import inspect
from collections.abc import Callable, ItemsView, KeysView, ValuesView
from contextvars import ContextVar, Token
from types import TracebackType
from typing import Any, ClassVar, Protocol

_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(value: str) -> Token[str]:
    return _request_id_var.set(value)


def reset_request_id(token: Token[str]) -> None:
    _request_id_var.reset(token)


def get_request_id() -> str:
    return _request_id_var.get()


class ContextFactory(Protocol):
    def __call__(
        self,
        func: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]: ...


class LoggingContext:
    _context_var: ClassVar[ContextVar[dict[str, Any] | None]] = ContextVar(
        "logging_context",
        default=None,
    )

    def __init__(self) -> None:
        self._previous_state: dict[str, Any] | None = None

    def __setitem__(self, key: str, value: Any) -> None:
        context = self.copy()
        context[key] = value
        self._context_var.set(context)

    def __getitem__(self, key: str) -> Any:
        context = self._get_context()
        if key not in context:
            raise KeyError(key)
        return context[key]

    def __delitem__(self, key: str) -> None:
        context = self.copy()
        context.pop(key, None)
        self._context_var.set(context)

    def __contains__(self, key: object) -> bool:
        return key in self._get_context()

    def __enter__(self) -> "LoggingContext":
        self._previous_state = self.copy()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._context_var.set(self._previous_state or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._get_context().get(key, default)

    def pop(self, key: str, default: Any = None) -> Any:
        context = self.copy()
        value = context.pop(key, default)
        self._context_var.set(context)
        return value

    def clear(self) -> None:
        self._context_var.set({})

    def keys(self) -> KeysView[str]:
        return self._get_context().keys()

    def values(self) -> ValuesView[Any]:
        return self._get_context().values()

    def items(self) -> ItemsView[str, Any]:
        return self._get_context().items()

    def copy(self) -> dict[str, Any]:
        return dict(self._get_context())

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls()[key] = value

    @classmethod
    def set_many(cls, **labels: Any) -> None:
        context = cls()
        for key, value in labels.items():
            context[key] = value

    @classmethod
    def get_context(cls) -> dict[str, Any]:
        return cls().copy()

    @classmethod
    def decorator(
        cls,
        context_factory: ContextFactory | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorate(func: Callable[..., Any]) -> Callable[..., Any]:
            if inspect.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    with cls() as context:
                        _set_labels(context, _build_labels(context_factory, func, args, kwargs))
                        return await func(*args, **kwargs)

                return async_wrapper

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with cls() as context:
                    _set_labels(context, _build_labels(context_factory, func, args, kwargs))
                    return func(*args, **kwargs)

            return wrapper

        return decorate

    def _get_context(self) -> dict[str, Any]:
        return self._context_var.get() or {}


def _build_labels(
    context_factory: ContextFactory | None,
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    if context_factory is None:
        return {}
    return context_factory(func, args, kwargs)


def _set_labels(context: LoggingContext, labels: dict[str, Any]) -> None:
    for key, value in labels.items():
        context[key] = value
