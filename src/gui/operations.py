from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Callable, TypeVar

from anki.utils import point_version
from aqt import mw
from aqt.operations import QueryOp

has_serialized_ops = point_version() >= 231000


T = TypeVar("T")


class AddonQueryOp(QueryOp[T]):
    def without_collection(self) -> QueryOp[T]:
        if has_serialized_ops:
            return super().without_collection()
        return self


def run_task_in_background(
    task: Callable,
    on_done: Callable[[Future], None] | None = None,
    args: dict[str, Any] | None = None,
    uses_collection: bool = True,
) -> Future:
    kwargs: dict[str, Any] = dict(task=task, on_done=on_done, args=args)
    if has_serialized_ops:
        kwargs["uses_collection"] = uses_collection
    return mw.taskman.run_in_background(**kwargs)
