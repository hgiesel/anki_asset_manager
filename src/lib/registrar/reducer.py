from typing import List, Callable

from ...config_types import (
    LabelReducer,
    DEFAULT_REDUCER,
)

from ..interface import make_reducer


_label_reducers: List[LabelReducer] = []

def make_and_register_reducer(
    label: str,
    reducer: Callable[[List[str]], str],
) -> LabelReducer:
    register_reducer(make_reducer(
        label = label,
        reducer = reducer,
    ))

def register_reducer(redux: LabelReducer) -> None:
    _label_reducers.append(redux)

def get_reducer(label: str) -> LabelReducer:
    try:
        return next(filter(lambda v: v.label == label, _label_reducers))
    except StopIteration:
        return DEFAULT_REDUCER

def has_reducer(label: str) -> bool:
    try:
        next(filter(lambda v: v.label == label, _label_reducers))
        return True
    except StopIteration:
        return False
