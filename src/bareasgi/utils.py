from collections.abc import AsyncIterable, AsyncIterator


async def aiter(*args):
    """aiter(async_iterable) -> async_iterator
    aiter(async_callable, sentinel) -> async_iterator
    An async version of the iter() builtin.
    """
    lenargs = len(args)
    if lenargs != 1 and lenargs != 2:
        raise TypeError(f'aiter expected 1 or 2 arguments, got {lenargs}')
    if lenargs == 1:
        obj, = args
        if not isinstance(obj, AsyncIterable):
            raise TypeError(
                f'aiter expected an AsyncIterable, got {type(obj)}')
        async for i in obj.__aiter__():
            yield i
        return
    # lenargs == 2
    async_callable, sentinel = args
    while True:
        value = await async_callable()
        if value == sentinel:
            break
        yield value


async def anext(*args):
    """anext(async_iterator[, default])
    Return the next item from the async iterator.
    If default is given and the iterator is exhausted,
    it is returned instead of raising StopAsyncIteration.
    """
    lenargs = len(args)
    if lenargs != 1 and lenargs != 2:
        raise TypeError(f'anext expected 1 or 2 arguments, got {lenargs}')
    ait = args[0]
    if not isinstance(ait, AsyncIterator):
        raise TypeError(f'anext expected an AsyncIterable, got {type(ait)}')
    anxt = ait.__anext__
    try:
        return await anxt()
    except StopAsyncIteration:
        if lenargs == 1:
            raise
        return args[1]  # default
