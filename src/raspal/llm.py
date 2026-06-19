import json
import re
from typing import Any

from raspal.models import ChainStep, LLMConfig


class LLMExtractor:
    PROMPT_TEMPLATES = {
        "product": "Extract product info: name, brand, price, currency, "
                    "description, availability, specifications.",
        "article": "Extract article info: title, author, date, "
                    "summary, and key points.",
        "person": "Extract person info: name, role, organization, "
                    "location, and contact details.",
        "review": "Extract review info: rating, reviewer, date, "
                    "pros, cons, and overall sentiment.",
        "event": "Extract event info: name, date, location, "
                    "organizer, and description.",
        "generic": "Extract structured information from the following text.",
    }

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()

    def extract(self, text: str, config: LLMConfig | None = None) -> dict:
        cfg = config or self.config
        return self._execute(text, cfg)

    def extract_batch(self, texts: list[str], config: LLMConfig | None = None) -> list[dict]:
        cfg = config or self.config
        return [self._execute(t, cfg) for t in texts]

    def extract_chain(self, text: str, chain: list[ChainStep]) -> dict:
        result: dict[str, Any] = {}
        current = text
        for step in chain:
            cfg = LLMConfig(
                model=step.model or self.config.model,
                prompt=step.prompt,
                output_schema=step.output_schema,
                template=step.template,
                temperature=step.temperature,
            )
            step_result = self._execute(current, cfg)
            result[step.name] = step_result
            if step.output_key and step_result.get("raw") is None:
                current = json.dumps(step_result)
        return result

    def _execute(self, text: str, cfg: LLMConfig) -> dict:
        prompt = self._build_prompt(text, cfg)
        response = self._ollama_chat(cfg.model, prompt, cfg.temperature)
        return self._parse_response(response, cfg.output_schema, cfg.strict)

    def _build_prompt(self, text: str, cfg: LLMConfig) -> str:
        template_name = cfg.template or "generic"
        base = cfg.prompt or self.PROMPT_TEMPLATES.get(
            template_name, self.PROMPT_TEMPLATES["generic"]
        )

        schema_instruction = ""
        if cfg.output_schema:
            schema_str = json.dumps(cfg.output_schema, indent=2)
            schema_instruction = (
                f"\n\nReturn ONLY a valid JSON object matching this schema:\n{schema_str}"
            )

        strict_instruction = ""
        if cfg.strict:
            strict_instruction = (
                "\n\nRespond with ONLY the JSON object, no markdown, no explanation."
            )

        return f"{base}{schema_instruction}{strict_instruction}\n\nTEXT:\n{text[:16000]}"

    def _ollama_chat(self, model: str, prompt: str, temperature: float = 0.0) -> str:
        import ollama

        resp = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature},
        )
        return resp["message"]["content"]

    def _parse_response(self, response: str, schema: dict | None, strict: bool = False) -> dict:
        if schema:
            try:
                cleaned = self._clean_json(response)
                parsed = json.loads(cleaned)
                if strict:
                    parsed = {k: parsed.get(k) for k in schema}
                return parsed
            except (ValueError, json.JSONDecodeError):
                pass
        return {"raw": response}

    @staticmethod
    def _clean_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
        return text
