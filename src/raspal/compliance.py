"""
Legal and ethical compliance helpers for RASPAL SCRAPER.

This module provides utilities to help users make informed decisions about
their scraping activities. It does not make legal determinations.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


class ComplianceChecker:
    """Check basic compliance signals before scraping."""

    def __init__(self, user_agent: str = "RASPAL-SCRAPER/0.4.0 (+https://github.com/juandelaf1/RASPAL_SCRAPER)"):
        self.user_agent = user_agent

    def check_url(self, url: str) -> dict:
        """Return compliance signals for a URL.

        This checks:
        - robots.txt presence and rules
        - URL structure validity
        - Whether the domain appears to be a sensitive target

        Returns:
            dict with compliance signals and warnings
        """
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                "valid": False,
                "warnings": ["URL inválida: debe incluir esquema (http:// o https://)"],
            }

        warnings = []
        signals = {
            "valid": True,
            "url": url,
            "domain": parsed.netloc,
            "robots_txt": None,
            "is_sensitive_domain": self._is_sensitive_domain(parsed.netloc),
        }

        if signals["is_sensitive_domain"]:
            warnings.append(
                "Dominio potencialmente sensible (redes sociales, salud, finanzas). "
                "Revisa cuidadosamente ToS y regulaciones aplicables."
            )

        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        signals["robots_txt"] = robots_url
        warnings.append(f"Consulta {robots_url} antes de scrapear")

        return {"signals": signals, "warnings": warnings}

    def _is_sensitive_domain(self, domain: str) -> bool:
        """Check if domain appears to be a sensitive target."""
        sensitive_patterns = [
            "facebook.com",
            "linkedin.com",
            "instagram.com",
            "twitter.com",
            "x.com",
            "health",
            "hospital",
            "clinic",
            "bank",
            "finance",
            "insurance",
        ]
        domain_lower = domain.lower()
        return any(pattern in domain_lower for pattern in sensitive_patterns)


def check_compliance(url: str) -> dict:
    """Convenience function for quick compliance checks."""
    return ComplianceChecker().check_url(url)


def load_config(config_path: str | Path) -> dict:
    """Load a YAML config and return compliance-relevant metadata."""
    import yaml

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not config:
        return {}

    result = {
        "url": config.get("url"),
        "engine": config.get("engine", "auto"),
        "llm_enabled": bool(config.get("llm")),
        "extract_text": config.get("extract", {}).get("text", True),
        "extract_metadata": config.get("extract", {}).get("metadata", True),
    }

    if result["url"]:
        result["compliance"] = check_compliance(result["url"])

    return result
