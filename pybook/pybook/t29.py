def sort_words(words: list):
    words.sort(key=lambda x: (len(x), x))
    return words
