"""Fail-closed PII detection and redaction primitives.

Built-in recognizers are starter recognizers, not a comprehensive DLP system.
"""
from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol


class RedactionError(RuntimeError):
    """Raised when detection or policy evaluation cannot complete safely."""


class PiiPolicyViolation(RedactionError):
    """Raised when a configured policy blocks a payload containing PII."""


@dataclass(frozen=True, slots=True)
class Detection:
    entity: str
    start: int
    end: int
    score: float
    text: str


class Detector(Protocol):
    def detect(self, text: str) -> list[Detection]: ...


@dataclass(frozen=True, slots=True)
class _Pattern:
    entity: str
    pattern: re.Pattern[str]
    score: float
    validator: Callable[[str], bool] | None = None


def _luhn(value: str) -> bool:
    digits = [int(ch) for ch in value if ch.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


class RegexDetector:
    """Dependency-free recognizers for a limited set of common entity types."""

    def __init__(self) -> None:
        self._patterns = (
            _Pattern("EMAIL", re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I), 0.99),
            _Pattern("CREDIT_CARD", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), 0.99, _luhn),
            _Pattern("PHONE_NUMBER", re.compile(r"(?<!\w)(?:\+?\d{1,3}[ .-]?)?(?:\(?\d{2,4}\)?[ .-]?)\d{3,4}[ .-]?\d{3,4}(?!\w)"), 0.70),
            _Pattern("IP_ADDRESS", re.compile(r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\d.])"), 0.95),
        )

    def detect(self, text: str) -> list[Detection]:
        if not isinstance(text, str):
            raise TypeError("PII detector input must be text")
        found: list[Detection] = []
        for item in self._patterns:
            for match in item.pattern.finditer(text):
                value = match.group(0)
                if item.validator is not None and not item.validator(value):
                    continue
                if item.entity == "PHONE_NUMBER":
                    digits = sum(character.isdigit() for character in value)
                    left = text[max(0, match.start() - 3):match.start()]
                    right = text[match.end():match.end() + 3]
                    # Do not classify a substring of a longer card-like digit run as a phone.
                    if not 7 <= digits <= 15:
                        continue
                    if re.search(r"[0-9][ .-]?$", left) or re.match(r"[ .-]?[0-9]", right):
                        continue
                found.append(Detection(item.entity, match.start(), match.end(), item.score, value))
        return found


class RedactionEngine:
    """Policy-driven redaction engine; detector failures never return raw input."""

    def __init__(
        self,
        detectors: Iterable[Detector] | None = None,
        *,
        entities: set[str] | None = None,
        action: str = "redact",
        fail_closed: bool = True,
        hmac_key: bytes | None = None,
    ) -> None:
        if action not in {"redact", "block", "pseudonymize"}:
            raise ValueError("action must be redact, block, or pseudonymize")
        self.detectors = tuple(detectors if detectors is not None else (RegexDetector(),))
        if not self.detectors:
            raise ValueError("at least one detector is required")
        self.entities = {entity.upper() for entity in entities} if entities else None
        self.action = action
        self.fail_closed = fail_closed
        self.hmac_key = hmac_key
        if action == "pseudonymize" and not hmac_key:
            raise ValueError("pseudonymize requires a non-empty HMAC key")

    def detect(self, text: str) -> list[Detection]:
        if not isinstance(text, str):
            raise TypeError("redaction input must be text")
        try:
            detections = [item for detector in self.detectors for item in detector.detect(text)]
            if self.entities is not None:
                detections = [item for item in detections if item.entity.upper() in self.entities]
            for item in detections:
                if item.start < 0 or item.end > len(text) or item.start >= item.end:
                    raise ValueError("detector returned an invalid span")
                if text[item.start:item.end] != item.text:
                    raise ValueError("detector span does not match source text")
            return self._resolve_overlaps(detections)
        except Exception as exc:
            if self.fail_closed:
                raise RedactionError("PII detection failed; payload withheld") from exc
            raise RedactionError("PII detection failed") from exc

    @staticmethod
    def _resolve_overlaps(detections: list[Detection]) -> list[Detection]:
        ordered = sorted(detections, key=lambda item: (item.start, -(item.end - item.start), -item.score))
        selected: list[Detection] = []
        for item in ordered:
            if selected and item.start < selected[-1].end:
                continue
            selected.append(item)
        return selected

    def redact(self, text: str) -> str:
        detections = self.detect(text)
        if self.action == "block" and detections:
            raise PiiPolicyViolation("payload blocked by PII policy")
        result = text
        for index, item in reversed(list(enumerate(detections, start=1))):
            if self.action == "pseudonymize":
                token = hmac.new(self.hmac_key or b"", item.text.encode(), hashlib.sha256).hexdigest()[:16]
                replacement = f"[{item.entity}_{token}]"
            else:
                replacement = f"[{item.entity}_{index}]"
            result = result[:item.start] + replacement + result[item.end:]
        return result

    def redact_json(self, value: object) -> object:
        """Recursively redact strings in JSON-compatible values."""
        if isinstance(value, str):
            return self.redact(value)
        if isinstance(value, list):
            return [self.redact_json(item) for item in value]
        if isinstance(value, dict):
            if not all(isinstance(key, str) for key in value):
                raise RedactionError("non-string JSON object key; payload withheld")
            return {key: self.redact_json(item) for key, item in value.items()}
        if value is None or isinstance(value, (bool, int, float)):
            return value
        raise RedactionError("unsupported JSON value; payload withheld")
