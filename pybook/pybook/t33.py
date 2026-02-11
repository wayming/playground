def count_words(text: str):
    words = []
    for l in text.splitlines():
        words.extend([x for x in l.split() if x.isalnum()])
    return len(words)
