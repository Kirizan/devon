import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from huggingface_hub import HfApi, snapshot_download

from devon.models.model_info import ModelMetadata
from devon.sources.base import ModelSource
from devon.sources.registry import register_source

logger = logging.getLogger(__name__)


@register_source
class HuggingFaceSource(ModelSource):
    """HuggingFace Hub model source."""

    def __init__(self):
        self.api = HfApi()

    @classmethod
    def name(cls) -> str:
        return "huggingface"

    @classmethod
    def is_available(cls) -> bool:
        try:
            api = HfApi()
            list(api.list_models(limit=1))
            return True
        except Exception:
            return False

    def search(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
    ) -> List[ModelMetadata]:
        """Search HuggingFace models with filters."""
        filters = filters or {}

        # Build HF API kwargs
        hf_kwargs = self._build_hf_kwargs(filters)

        # Search with extra results for post-filtering
        models = list(
            self.api.list_models(
                search=query,
                limit=limit * 2,
                sort="downloads",
                direction=-1,
                cardData=True,
                **hf_kwargs,
            )
        )

        # Convert and post-filter
        results = []
        for model in models:
            metadata = self._convert_to_metadata(model)

            if self._matches_filters(metadata, filters):
                results.append(metadata)

                if len(results) >= limit:
                    break

        return results

    def _build_hf_kwargs(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert filters to HF list_models keyword arguments."""
        hf_kwargs: Dict[str, Any] = {}

        if "author" in filters:
            hf_kwargs["author"] = filters["author"]

        if "format" in filters:
            format_map = {
                "gguf": "gguf",
                "safetensors": "safetensors",
                "pytorch": "pytorch",
            }
            formats = filters["format"]
            if isinstance(formats, str):
                formats = [formats]
            hf_kwargs["library"] = [format_map.get(f, f) for f in formats]

        if "task" in filters:
            hf_kwargs["pipeline_tag"] = filters["task"]

        if "tags" in filters:
            hf_kwargs["tags"] = filters["tags"]

        return hf_kwargs

    def _matches_filters(self, metadata: ModelMetadata, filters: Dict[str, Any]) -> bool:
        """Check post-search filters."""
        # Parameter count filter
        if "params" in filters:
            target = self._parse_params(filters["params"])
            if metadata.parameter_count:
                lower, upper = target * 0.8, target * 1.2
                if not (lower <= metadata.parameter_count <= upper):
                    return False

        # Size filter
        if "size" in filters:
            constraint = self._parse_size_constraint(filters["size"])
            if constraint and not self._size_matches(metadata.total_size_bytes, constraint):
                return False

        return True

    def _parse_params(self, params_str: str) -> int:
        """Parse '30b' to 30."""
        match = re.match(r"(\d+)b?", params_str.lower())
        return int(match.group(1)) if match else 0

    def _parse_size_constraint(self, size_str: str) -> Optional[Dict]:
        """Parse '<100gb' to constraint dict."""
        match = re.match(r"([<>]=?)(\d+)(gb|mb|tb)", size_str.lower())
        if not match:
            return None

        op, value, unit = match.groups()
        multipliers = {"mb": 1024**2, "gb": 1024**3, "tb": 1024**4}
        return {"operator": op, "size": int(value) * multipliers[unit]}

    def _size_matches(self, actual: int, constraint: Dict) -> bool:
        """Check if size matches constraint."""
        op, target = constraint["operator"], constraint["size"]

        if op == "<":
            return actual < target
        elif op == "<=":
            return actual <= target
        elif op == ">":
            return actual > target
        elif op == ">=":
            return actual >= target
        return True

    def _convert_to_metadata(self, hf_model) -> ModelMetadata:
        """Convert HF ModelInfo to ModelMetadata."""
        param_count = self._extract_param_count(hf_model)
        total_size = sum(
            s.size for s in (hf_model.siblings or []) if hasattr(s, "size") and s.size
        )
        architecture = self._extract_architecture(hf_model.tags or [])
        formats = self._detect_formats(hf_model.siblings or [])
        quantization = self._detect_quantization(hf_model.tags or [], hf_model.modelId)

        card_data = hf_model.cardData if hasattr(hf_model, "cardData") else None
        model_license = None
        if card_data and isinstance(card_data, dict):
            model_license = card_data.get("license")

        return ModelMetadata(
            source="huggingface",
            model_id=hf_model.modelId,
            model_name=hf_model.modelId.split("/")[-1],
            author=hf_model.author or hf_model.modelId.split("/")[0],
            total_size_bytes=total_size,
            file_count=len(hf_model.siblings or []),
            parameter_count=param_count,
            architecture=architecture,
            format=formats,
            quantization=quantization,
            tags=hf_model.tags or [],
            license=model_license,
            downloads=hf_model.downloads or 0,
            likes=hf_model.likes or 0,
            created_at=hf_model.createdAt.isoformat() if hf_model.createdAt else "",
            updated_at=hf_model.lastModified.isoformat() if hf_model.lastModified else "",
            web_url=f"https://huggingface.co/{hf_model.modelId}",
            repo_url=f"https://huggingface.co/{hf_model.modelId}/tree/main",
        )

    def _extract_param_count(self, hf_model) -> Optional[int]:
        """Extract parameter count from tags or ID."""
        for tag in hf_model.tags or []:
            match = re.search(r"(\d+)b", tag.lower())
            if match:
                return int(match.group(1))

        match = re.search(r"(\d+)b", hf_model.modelId.lower())
        return int(match.group(1)) if match else None

    def _extract_architecture(self, tags: List[str]) -> Optional[str]:
        """Extract architecture from tags."""
        arch_keywords = ["llama", "qwen", "mistral", "gpt", "bert", "gemma"]
        for tag in tags:
            for arch in arch_keywords:
                if arch in tag.lower():
                    return arch
        return None

    def _detect_formats(self, siblings) -> List[str]:
        """Detect formats from file extensions."""
        formats = set()
        for sibling in siblings:
            filename = sibling.rfilename
            if filename.endswith(".safetensors"):
                formats.add("safetensors")
            elif filename.endswith(".bin"):
                formats.add("pytorch")
            elif filename.endswith(".gguf"):
                formats.add("gguf")
        return list(formats)

    def _detect_quantization(self, tags: List[str], model_id: str) -> Optional[str]:
        """Detect quantization from tags or ID."""
        quant_patterns = ["Q4_K_M", "Q5_K_M", "Q8_0", "fp16", "bf16", "int8", "int4"]
        text = " ".join(tags) + " " + model_id
        for pattern in quant_patterns:
            if pattern in text:
                return pattern
        return None

    def get_model_info(self, model_id: str) -> ModelMetadata:
        """Get detailed model information."""
        hf_model = self.api.model_info(model_id, files_metadata=True)
        return self._convert_to_metadata(hf_model)

    def download_model(
        self,
        model_id: str,
        dest_path: str,
        progress_callback=None,
    ) -> List[str]:
        """Download model using HF snapshot_download."""
        downloaded_path = snapshot_download(
            repo_id=model_id,
            local_dir=dest_path,
            resume_download=True,
        )

        # Return list of files
        downloaded_files = []
        for item in Path(downloaded_path).rglob("*"):
            if item.is_file():
                downloaded_files.append(str(item.relative_to(downloaded_path)))

        return downloaded_files
