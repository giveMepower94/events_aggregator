def seat_exists_in_pattern(seat: str, seats_pattern: str) -> bool:
    for chunk in seats_pattern.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue

        section = chunk[0]
        range_part = chunk[1:]

        if "-" not in range_part:
            continue

        start_str, end_str = range_part.split("-", maxsplit=1)

        try:
            start = int(start_str)
            end = int(end_str)
        except ValueError:
            continue

        if not seat.startswith(section):
            continue

        seat_number_str = seat[len(section):]
        if not seat_number_str.isdigit():
            return False

        seat_number = int(seat_number_str)
        return start <= seat_number <= end

    return False
