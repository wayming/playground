def t98_merge_intervals(intervals: list[list[int]]):

    results = []

    if not intervals:
        return results

    intervals.sort()
    slow = []
    for fast in intervals:
        if slow == []:
            slow = fast
            continue

        if fast[0] <= slow[-1]:
            slow = [slow[0], max(slow[-1], fast[-1])]
        else:
            results.append(slow)
            slow = fast
    results.append(slow)
    return results
