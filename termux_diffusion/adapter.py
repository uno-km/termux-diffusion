"""
termux_diffusion.adapter
=========================
AMEVA Component Protocol v1 — Orchestrator Adapter (v0.8.1 호환)
"""
from __future__ import annotations

from typing import Any, AsyncIterator

from ameva_component.adapter_base import BaseOrchestratorAdapter
from ameva_component.exceptions import OperationNotSupported
from termux_diffusion.control.component import DiffusionControl


class DiffusionOrchestratorAdapter(BaseOrchestratorAdapter):
    """Diffusion Orchestrator Adapter.

    이미지 생성은 sd-cli subprocess를 통해 수행됩니다.
    infer()는 OPERATION_NOT_SUPPORTED — generate() REST endpoint를 사용하십시오.
    """

    COMPONENT_ID = "termux-diffusion"

    def __init__(self, control: DiffusionControl | None = None) -> None:
        self._control = control or DiffusionControl()

    async def infer(self, request: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        """Diffusion generation은 REST endpoint /generate 를 통해 수행됩니다.
        Orchestrator 직접 streaming은 미지원 — OperationNotSupported를 발생시킵니다.

        P0-2: yield 방식은 상위 소비자가 Frame을 정상으로 처리할 위험이 있어 raise로 변경.
        """
        raise OperationNotSupported(operation="infer", component_id=self.COMPONENT_ID)
        yield  # type: ignore[misc]


def create_adapter() -> DiffusionOrchestratorAdapter:
    """Entry Point Factory."""
    return DiffusionOrchestratorAdapter()
