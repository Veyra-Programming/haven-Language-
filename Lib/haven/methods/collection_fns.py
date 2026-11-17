"""
Haven Standard Library - Collection & Functional Methods
Standard: Open Digital Continuity Standard (ODCS) & Functional Data Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import itertools
import random
from typing import List, Dict, Any, Callable, Tuple, Optional, Sequence, Set, Iterable


def chunk_list(items: Sequence[Any], size: int) -> List[List[Any]]:
    """Splits collection into fixed-size chunks."""
    if size <= 0:
        raise ValueError("Chunk size must be positive.")
    return [list(items[i : i + size]) for i in range(0, len(items), size)]


def window_list(items: Sequence[Any], size: int, step: int = 1) -> List[List[Any]]:
    """Computes sliding windows of given size and step."""
    if size <= 0 or step <= 0:
        raise ValueError("Window size and step must be positive.")
    return [list(items[i : i + size]) for i in range(0, len(items) - size + 1, step)]


def flatten_list(nested: Iterable[Any]) -> List[Any]:
    """Flattens arbitrarily nested lists/tuples into a flat list."""
    flat = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            flat.extend(flatten_list(item))
        else:
            flat.append(item)
    return flat


def unique_list(items: Sequence[Any]) -> List[Any]:
    """Returns elements with duplicates removed while preserving order."""
    seen = set()
    result = []
    for item in items:
        # If unhashable (dict/list), fall back
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError:
            if item not in result:
                result.append(item)
    return result


def frequencies_map(items: Iterable[Any]) -> Dict[Any, int]:
    """Counts occurrences of each unique element."""
    counts: Dict[Any, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def group_by_key(items: Iterable[Any], key_fn: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    """Groups items into a dictionary bucketed by key_fn(item)."""
    groups: Dict[Any, List[Any]] = {}
    for item in items:
        k = key_fn(item)
        if k not in groups:
            groups[k] = []
        groups[k].append(item)
    return groups


def partition_list(items: Iterable[Any], predicate: Callable[[Any], bool]) -> Tuple[List[Any], List[Any]]:
    """Splits items into two lists: (truthy_matches, falsy_matches)."""
    passed, failed = [], []
    for item in items:
        if predicate(item):
            passed.append(item)
        else:
            failed.append(item)
    return passed, failed


def zip_with_fn(xs: Sequence[Any], ys: Sequence[Any], fn: Callable[[Any, Any], Any]) -> List[Any]:
    """Combines two sequences element-wise with a combiner function."""
    return [fn(x, y) for x, y in zip(xs, ys)]


def intersperse_val(items: Sequence[Any], sep: Any) -> List[Any]:
    """Inserts a separator between elements of a sequence."""
    if not items:
        return []
    res = [items[0]]
    for item in items[1:]:
        res.append(sep)
        res.append(item)
    return res


def compact_list(items: Iterable[Any]) -> List[Any]:
    """Filters out None and falsy values."""
    return [x for x in items if x]


def find_first(items: Iterable[Any], predicate: Callable[[Any], bool], default: Any = None) -> Any:
    """Finds the first item satisfying predicate."""
    for item in items:
        if predicate(item):
            return item
    return default


def find_last(items: Sequence[Any], predicate: Callable[[Any], bool], default: Any = None) -> Any:
    """Finds the last item satisfying predicate."""
    for item in reversed(items):
        if predicate(item):
            return item
    return default


def find_index(items: Sequence[Any], predicate: Callable[[Any], bool]) -> int:
    """Returns index of first item matching predicate, or -1 if not found."""
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return -1


def take_while_fn(items: Iterable[Any], predicate: Callable[[Any], bool]) -> List[Any]:
    """Takes items while predicate is true, stops at first failure."""
    res = []
    for item in items:
        if predicate(item):
            res.append(item)
        else:
            break
    return res


def drop_while_fn(items: Iterable[Any], predicate: Callable[[Any], bool]) -> List[Any]:
    """Drops items while predicate is true, then returns remaining."""
    it = iter(items)
    res = []
    for item in it:
        if not predicate(item):
            res.append(item)
            break
    res.extend(it)
    return res


def shuffle_list(items: Sequence[Any]) -> List[Any]:
    """Returns a shuffled shallow copy of the collection."""
    res = list(items)
    random.shuffle(res)
    return res


def sample_list(items: Sequence[Any], k: int) -> List[Any]:
    """Draws k random items without replacement."""
    return random.sample(items, min(k, len(items)))


def cartesian_product(xs: Iterable[Any], ys: Iterable[Any]) -> List[Tuple[Any, Any]]:
    """Computes Cartesian product of two collections."""
    return list(itertools.product(xs, ys))


def permutations_list(items: Sequence[Any], r: Optional[int] = None) -> List[Tuple[Any, ...]]:
    """Generates all r-length permutations of elements."""
    return list(itertools.permutations(items, r))


def combinations_list(items: Sequence[Any], r: int) -> List[Tuple[Any, ...]]:
    """Generates all r-length combinations of elements."""
    return list(itertools.combinations(items, r))


def intersect_sets(a: Iterable[Any], b: Iterable[Any]) -> List[Any]:
    """Returns intersection of two collections."""
    return list(set(a) & set(b))


def union_sets(a: Iterable[Any], b: Iterable[Any]) -> List[Any]:
    """Returns union of two collections."""
    return list(set(a) | set(b))


def difference_sets(a: Iterable[Any], b: Iterable[Any]) -> List[Any]:
    """Returns set difference (a - b)."""
    return list(set(a) - set(b))


def symmetric_difference_sets(a: Iterable[Any], b: Iterable[Any]) -> List[Any]:
    """Returns symmetric difference between two collections."""
    return list(set(a) ^ set(b))


def is_subset_of(a: Iterable[Any], b: Iterable[Any]) -> bool:
    """Checks if a is a subset of b."""
    return set(a).issubset(set(b))


def is_superset_of(a: Iterable[Any], b: Iterable[Any]) -> bool:
    """Checks if a is a superset of b."""
    return set(a).issuperset(set(b))


def key_by_fn(items: Iterable[Any], key_fn: Callable[[Any], Any]) -> Dict[Any, Any]:
    """Indexes items by key_fn(item) -> item."""
    return {key_fn(item): item for item in items}


def map_values_dict(d: Dict[Any, Any], fn: Callable[[Any], Any]) -> Dict[Any, Any]:
    """Maps a function over the values of a dictionary."""
    return {k: fn(v) for k, v in d.items()}


def filter_keys_dict(d: Dict[Any, Any], predicate: Callable[[Any], bool]) -> Dict[Any, Any]:
    """Filters dictionary entries by key."""
    return {k: v for k, v in d.items() if predicate(k)}


def filter_values_dict(d: Dict[Any, Any], predicate: Callable[[Any], bool]) -> Dict[Any, Any]:
    """Filters dictionary entries by value."""
    return {k: v for k, v in d.items() if predicate(v)}


def invert_dict(d: Dict[Any, Any]) -> Dict[Any, Any]:
    """Inverts keys and values of a dictionary."""
    return {v: k for k, v in d.items()}


def merge_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merges multiple dictionaries in order."""
    res = {}
    for d in dicts:
        res.update(d)
    return res


def pluck_key(items: Iterable[Dict[str, Any]], key: str, default: Any = None) -> List[Any]:
    """Extracts a specific key from a collection of dictionaries."""
    return [d.get(key, default) for d in items]


def sort_by_key(items: Sequence[Any], key_fn: Callable[[Any], Any], reverse: bool = False) -> List[Any]:
    """Sorts collection by key_fn."""
    return sorted(items, key=key_fn, reverse=reverse)
