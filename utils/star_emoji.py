def get_star_display(stars: int) -> str:
    if stars <= 0:
        return "☆"
    return "⭐" * stars
