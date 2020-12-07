from typing import List, Any
import bisect


def _insort(a: List, x: Any) -> bool:
    """insert x into a if not currently there"""
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        # don't insert
        return False
    a.insert(i, x)
    return True
