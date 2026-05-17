import asyncio
import re

from toolkitsy.logger._correlation_id import (
    get_correlation_id,
    set_correlation_id,
)

UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def test_set_explicit_value_returns_same_value():
    set_correlation_id("req-abc-123")
    assert get_correlation_id() == "req-abc-123"


def test_set_with_no_arg_auto_generates_uuid4():
    set_correlation_id(None)
    cid = get_correlation_id()
    assert UUID4_RE.match(cid), f"expected uuid4, got {cid!r}"


def test_set_with_no_args_at_all_auto_generates_uuid4():
    set_correlation_id()
    cid = get_correlation_id()
    assert UUID4_RE.match(cid)


def test_get_without_set_auto_generates_and_persists():
    async def runner():
        first = get_correlation_id()
        second = get_correlation_id()
        return first, second

    first, second = asyncio.run(runner())
    assert UUID4_RE.match(first)
    assert first == second


def test_correlation_id_isolated_per_async_task():
    async def child(label, store):
        set_correlation_id(label)
        await asyncio.sleep(0)
        store.append((label, get_correlation_id()))

    async def runner():
        results = []
        await asyncio.gather(
            child("task-a", results),
            child("task-b", results),
        )
        return results

    results = asyncio.run(runner())
    by_label = dict(results)
    assert by_label["task-a"] == "task-a"
    assert by_label["task-b"] == "task-b"


def test_set_returns_the_value_it_stored():
    returned = set_correlation_id("explicit-value")
    assert returned == "explicit-value"
    auto = set_correlation_id()
    assert UUID4_RE.match(auto)
    assert auto == get_correlation_id()
