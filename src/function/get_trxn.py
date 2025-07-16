import re
from collections import Counter
from typing import Dict, List, Optional, Tuple


currency_dictionary: Dict[str, str] = {
    "rm": "MYR",
    "Rm": "MYR",
    "RM": "MYR",
}


def match_date_format(text: str) -> List[str]:
    date_patterns = [
        r"\b(\d{4})/(\d{1,2})/(\d{1,2})\b",
        r"\b(\d{2})/(\d{1,2})/(\d{1,2})\b",
        r"\b(\d{1,2})\s([A-Za-z]{3})\s(\d{2,4})\b",
        r"\b([A-Za-z]{3})\s(\d{1,2}),\s(\d{2,4})\b",
        r"\b([A-Za-z]+)\s(\d{1,2}),\s(\d{4})\b",
        r"\b(\d{1,2})\s([A-Za-z]+)\s(\d{4})\b",
        r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
        r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b",
        r"\b(20[0-4][0-9]|2050)(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])\b",
        r"\b([0-4][0-9]|50)(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])\b",
        r"\b(\d{1,2})/(\d{1,2})/(\d{2})\s(\d{1,2}):(\d{2})\s(AM|PM)\b",
        r"\b(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})\b",
        r"\b([A-Za-z]+),\s(\d{1,2})\s([A-Za-z]+)\s(\d{4})\b",
        r"\b([A-Za-z]+),s(d{1,2})s([A-Za-z]+)s(d{4})\b",
        r"\b([A-Za-z]+),\s([A-Za-z]{3})\s(\d{1,2}),\s(\d{4})\b",
        r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b",
        r"\b(\d{4})\.(\d{1,2})\.(\d{1,2})\b",
        r"\b(O\d{1,2})([A-Za-z]{3})(20[0-4][0-9]|2050)\b",
        r"\b(0[1-9]|[12][0-9]|3[01])([A-Za-z]{3})(20[0-4][0-9]|2050)\b",
        r"\b(0[1-9]|[12][0-9]|3[01])([A-Za-z]{4})(20[0-4][0-9]|2050)\b",
        r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b"
    ]
    pattern = re.compile("|".join(date_patterns))
    return pattern.findall(text)


def validate_time(text: str) -> List[str]:
    time_patterns = [
        r"\b(0[1-9]|1[0-2]):([0-5][0-9])(AM|PM)\b",
        r"\b(0[1-9]|1[0-2]):([0-5][0-9])\b",
        r"\b(0[0-2]|1[0-9]):([0-5][0-9])\b",
        r"\b(\d{2}):(\d{2})\b"
    ]
    pattern = re.compile("|".join(time_patterns))
    return pattern.findall(text)


def match_currency(text: str) -> Optional[str]:
    alphanum = re.findall(r"[a-zA-Z]", text.lower())
    key = ''.join(alphanum)
    return currency_dictionary.get(key)


def match_petrol(text: str) -> str:
    petronas = ["primax", "primax95", "primax 95", "primax97", "primax 97", "euro5", "euro 5", "ngv"]
    caltex = ["techron95", "95techron"]
    shell = [
        "fuelsave95", "fuelsave 95", "vpower97", "vpower 97",
        "fuelsavediesel", "fuelsave diesel", "vpowerdiesel", "vpower diesel"
    ]
    all_products = set(petronas + caltex + shell)
    for line in text.split("\n"):
        clean = ''.join(re.findall(r"[a-zA-Z0-9]", line.lower()))
        for product in all_products:
            if product.replace(" ", "") in clean:
                return line
    return ""


def most_frequent(arr: List[str]) -> Optional[str]:
    if not arr:
        return None
    counter = Counter(arr)
    return counter.most_common(1)[0][0]


def match_total(text: str) -> Dict[str, object]:
    total_patterns = [
        r"\b(RM|rm|Rm)?\s?(\d{1,4})(\.|,)\s?(\d{2})\b"
    ]
    pattern = re.compile("|".join(total_patterns))
    matches = pattern.findall(text)
    all_totals = [''.join(match) for match in matches]
    most_common_total = most_frequent(all_totals)
    if most_common_total:
        numeric_only = ''.join(re.findall(r"[0-9.]", most_common_total))
        return {"total": float(numeric_only), "amount": most_common_total}
    return {"total": 0, "amount": ""}


def get_trx_details(text: str) -> Dict[str, object]:
    matched_date = match_date_format(text)
    matched_time = validate_time(text)
    matched_fuel = match_petrol(text)
    total_info = match_total(text)

    return {
        "date": matched_date[0][0] if matched_date else "",
        "time": ":".join([x for x in matched_time[0] if x]) if matched_time else "",
        "fuelType": matched_fuel,
        "amount": total_info["total"],
        "total": total_info["amount"],
    }

