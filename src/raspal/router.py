from pathlib import Path

import yaml

from raspal.extractor import Extractor
from raspal.fetcher import Fetcher
from raspal.llm import LLMExtractor
from raspal.models import PipelineConfig
from raspal.pipeline import Pipeline
from raspal.queue import RequestQueue
from raspal.throttle import AutoThrottle


class Router:
    def __init__(self):
        self.throttle = AutoThrottle()
        self.fetcher = Fetcher(throttle=self.throttle)
        self.extractor = Extractor()
        self.llm = LLMExtractor()

    def run(self, config_path: str | Path) -> dict:
        with open(config_path) as f:
            raw = yaml.safe_load(f)

        config = PipelineConfig(**raw)

        if config.throttle:
            self.throttle = AutoThrottle(
                min_delay=config.throttle.min_delay,
                max_delay=config.throttle.max_delay,
                target_avg=config.throttle.target_avg,
            )
            self.fetcher.throttle = self.throttle

        fetch_result = self.fetcher.fetch(
            config.url, engine=config.engine, cache_ttl=config.cache_ttl
        )

        result = {
            "url": config.url,
            "status": fetch_result.status,
            "engine": fetch_result.engine,
            "cached": fetch_result.cached,
        }

        if config.extract.text and fetch_result.html:
            result["text"] = self.extractor.extract_text(fetch_result.html)

        if config.extract.metadata and fetch_result.html:
            result["metadata"] = self.extractor.extract_metadata(fetch_result.html)

        if config.extract.selectors and fetch_result.html:
            if config.extract.use_selectolax:
                result["selectors"] = self.extractor.extract_selectors_fast(
                    fetch_result.html, config.extract.selectors
                )
            else:
                result["selectors"] = self.extractor.extract_selectors(
                    fetch_result.html, config.extract.selectors
                )

        text = result.get("text")
        text_str = str(text) if text else ""
        if config.llm and text_str:
            result["llm_extraction"] = self.llm.extract(text_str, config.llm)
        if config.llm_chain and text_str:
            result["llm_chain"] = self.llm.extract_chain(text_str, config.llm_chain)

        return result

    def run_queue(
        self, config_path: str | Path,
        queue_path: str | Path = "raspal_queue.sqlite",
    ) -> Pipeline:
        with open(config_path) as f:
            raw = yaml.safe_load(f)

        config = PipelineConfig(**raw)
        queue = RequestQueue(queue_path)
        pipeline = Pipeline()

        while queue.pending_count() > 0:
            item = queue.pop()
            if item is None:
                break

            try:
                result = self.fetcher.fetch(item.url, engine=item.engine)
                if result.status != 200:
                    queue.retry(item, f"HTTP {result.status}")
                    continue

                data = {"status": result.status, "engine": result.engine}

                if config.extract.text and result.html:
                    data["text"] = self.extractor.extract_text(result.html)

                if config.extract.metadata and result.html:
                    data["metadata"] = self.extractor.extract_metadata(result.html)

                if config.extract.selectors and result.html:
                    if config.extract.use_selectolax:
                        data["selectors"] = self.extractor.extract_selectors_fast(
                            result.html, config.extract.selectors
                        )
                    else:
                        data["selectors"] = self.extractor.extract_selectors(
                            result.html, config.extract.selectors
                        )

                text = data.get("text")
                text_str = str(text) if text else ""
                if config.llm and text_str:
                    data["llm_extraction"] = self.llm.extract(text_str, config.llm)
                if config.llm_chain and text_str:
                    data["llm_chain"] = self.llm.extract_chain(text_str, config.llm_chain)

                pipeline.add(url=item.url, data=data)
                queue.complete(item)

            except Exception as e:
                queue.retry(item, str(e))

        queue.close()
        return pipeline
