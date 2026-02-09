import collections


def avg_by_user(scores):
    scoresByUser = collections.defaultdict(list)
    for user, score in scores:
        scoresByUser[user].append(score)
    print(scoresByUser)
    return {
        user: sum(userscores) / len(userscores)
        for user, userscores in scoresByUser.items()
    }
