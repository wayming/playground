import collections


def top_words(text: str, top: int):
    count = collections.Counter([x for x in text.split() if x.isalpha()])
    return [x[0] for x in count.most_common(top)]
