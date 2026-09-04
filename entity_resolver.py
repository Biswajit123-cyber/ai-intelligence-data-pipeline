import re
import unicodedata
from rapidfuzz.fuzz import ratio
from .models import EntityMapping

def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[,.'’]", " ", value)
    value = re.sub(r"\b(incorporated|inc|corp|corporation|ltd|limited|llc|co)\b", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

class EntityResolver:
    def __init__(self, canonical_names: list[str], threshold: float = 92.0):
        self.canonical = canonical_names
        self.threshold = threshold

    def resolve(self, raw: str, entity_type: str) -> EntityMapping:
        norm = normalize_name(raw)

        for name in self.canonical:
            if norm == normalize_name(name):
                return EntityMapping(
                    raw_name=raw, canonical_name=name, entity_type=entity_type,
                    method="exact_normalized", score=100.0
                )

        best_name, best_score = None, 0.0
        for name in self.canonical:
            score = ratio(norm, normalize_name(name))
            if score > best_score:
                best_name, best_score = name, score

        if best_name and best_score >= self.threshold:
            return EntityMapping(
                raw_name=raw, canonical_name=best_name, entity_type=entity_type,
                method="fuzzy", score=float(best_score)
            )

        return EntityMapping(
            raw_name=raw, canonical_name=raw.strip(), entity_type=entity_type,
            method="unresolved", score=float(best_score)
        )
