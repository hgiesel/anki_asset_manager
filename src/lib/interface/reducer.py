from typing import Callable, List

from ...config_types import (
    LabelReducer,
    DEFAULT_REDUCER,
)


def make_reducer(
    label: str,
    *,
    reducer: Callable[[List[str]], str],
) -> LabelReducer:
    return LabelReducer(
        label,
        reducer if reducer is not None else DEFAULT_REDUCER.reducer,
    )
