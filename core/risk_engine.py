def risk_score(perf, vol):
    score = 0

    if perf > 20:
        score -= 1
    if perf < -10:
        score += 2

    if vol > 3:
        score += 1

    return score


