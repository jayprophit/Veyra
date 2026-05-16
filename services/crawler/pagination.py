from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class PageSlice:
    page: int
    page_count: int
    page_size: int
    text: str
    has_previous: bool
    has_next: bool


def paginate_text(text: str, *, page: int = 1, page_size: int = 1200) -> PageSlice:
    if page_size < 200:
        raise ValueError("page_size must be at least 200 characters")

    normalized = text.strip()
    total_length = len(normalized)
    page_count = max(1, ceil(total_length / page_size))
    if page < 1 or page > page_count:
        raise ValueError("page is outside the available range")

    start = (page - 1) * page_size
    end = start + page_size
    chunk = normalized[start:end]

    return PageSlice(
        page=page,
        page_count=page_count,
        page_size=page_size,
        text=chunk,
        has_previous=page > 1,
        has_next=page < page_count,
    )
