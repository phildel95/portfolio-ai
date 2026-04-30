def recommendation(score, mode="equilibre"):
    if mode == "defensif":
        if score >= 2:
            return "📉 Réduire"
        elif score <= -2:
            return "⚠️ Sortir"
        return "🟡 Conserver"

    if mode == "equilibre":
        if score >= 3:
            return "📈 Renforcer"
        elif score <= -2:
            return "⚠️ Réduire"
        return "🟡 Conserver"

    if mode == "dynamique":
        if score >= 1:
            return "🚀 Laisser courir"
        return "🟡 Conserver"


