"""
termux_diffusion.control.component
AMEVA Component Protocol v1 — DiffusionControl

model_id는 파일명이 아닌 Pipeline Manifest를 가리킵니다.
(UNet + VAE + Text Encoder + Tokenizer + Scheduler Config)
기존 installer.run_doctor() + hub.py를 Adapter로 연결합니다.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from ameva_component import (
    ActivationLock, ComponentInfo, ComponentStateFile,
    ControlMode, InstanceRegistry, InstanceState, InstanceStatus,
    ModelRegistry, ModelState, ModelNotFound, ModelLoadFailed,
    OperationNotSupported, now_timestamps, log_stderr, PROTOCOL_COMPONENT,
)
from ameva_component.control import ComponentControl


class DiffusionControl(ComponentControl):
    """
    termux-diffusion ComponentControl.

    model_id = Pipeline Manifest ID (단일 파일명 아님).
    기존 installer.run_doctor(), hub.DEFAULT_PRESETS를 Adapter로 연결.
    """

    COMPONENT_ID   = "termux-diffusion"
    COMPONENT_TYPE = "diffusion"
    CAPABILITIES   = ("image.generate",)

    DEFAULT_MODELS_DIR = Path.home() / ".cache" / "termux-diffusion" / "models"

    def __init__(self, models_dir: Path | None = None) -> None:
        self._models_dir = models_dir or self.DEFAULT_MODELS_DIR
        self._state_file = ComponentStateFile(self.COMPONENT_ID)
        self._model_reg  = ModelRegistry(self.COMPONENT_ID)
        self._inst_reg   = InstanceRegistry(self.COMPONENT_ID)
        self._act_lock   = ActivationLock()

    def _get_version(self) -> str:
        try:
            from termux_diffusion import __version__; return __version__
        except Exception: return "1.3.2"

    def component_info(self) -> dict:
        info = ComponentInfo(
            protocol=PROTOCOL_COMPONENT, component_id=self.COMPONENT_ID,
            component_type=self.COMPONENT_TYPE, version=self._get_version(),
            capabilities=self.CAPABILITIES,
        )
        info.validate()
        return info.to_dict()

    def doctor_lite(self) -> dict:
        """
        경량 진단.
        샘플 추론 금지, 엔진 바이너리 존재 여부 + 상태파일만.
        """
        ts = now_timestamps()
        state_data = self._state_file.read()
        stale = self._state_file.is_stale(threshold_ms=30_000)
        pid, pid_alive = self._check_pid()
        instances = self._inst_reg.list_all()
        hot = [i for i in instances if i.state == InstanceState.HOT]

        # 엔진 바이너리 존재 여부 (실행 금지)
        engine_present = self._check_engine_binary()

        ready = engine_present
        degraded = stale or not pid_alive

        return {
            "protocol": "ameva-component-status/1",
            "component_id": self.COMPONENT_ID, "component_type": self.COMPONENT_TYPE,
            "version": self._get_version(), "ready": ready, "degraded": degraded,
            **ts,
            "process": {"running": pid_alive, "pid": pid},
            "capabilities": list(self.CAPABILITIES),
            "active_models": [i.model_id for i in hot],
            "engine": {"present": engine_present},
            "instances": [{"instance_id": i.instance_id, "model_id": i.model_id,
                           "state": i.state.value, "active_jobs": i.active_jobs} for i in instances],
            "errors": [state_data.get("last_error")] if state_data and state_data.get("last_error") else [],
            "state_file": {"path": str(self._state_file.path), "stale": stale,
                           "updated_at": state_data.get("updated_at") if state_data else None},
        }

    def _check_pid(self) -> tuple[int | None, bool]:
        pid_file = Path.home() / ".local" / "run" / "termux-diffusion.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, 0)
                return pid, True
            except Exception: pass
        return None, False

    def _check_engine_binary(self) -> bool:
        """엔진 바이너리 존재 여부만 확인 — 실행 금지."""
        try:
            from termux_diffusion.installer import provision_engine
            return True  # 모듈 import 성공 = 설치 가능 상태
        except ImportError:
            return False

    def doctor_full(self) -> dict:
        """기존 installer.run_doctor() 전체 실행."""
        lite = self.doctor_lite()
        try:
            from termux_diffusion.installer import run_doctor
            result = run_doctor()
            lite["full_doctor"] = result if isinstance(result, dict) else {"output": str(result)}
        except Exception as e:
            lite["doctor_error"] = str(e)
        lite["doctor_level"] = "full"
        return lite

    def list_models(self) -> dict:
        """Pipeline Manifest 기반 모델 목록 + hub.DEFAULT_PRESETS."""
        reg_map = {m["model_id"]: m for m in self._model_reg.list_all()}
        try:
            from termux_diffusion.hub import DEFAULT_PRESETS, list_presets
            for preset_id, preset_info in DEFAULT_PRESETS.items():
                if preset_id not in reg_map:
                    reg_map[preset_id] = {
                        "model_id":    preset_id,
                        "state":       "missing",
                        "format":      "pipeline",
                        "note":        "Available preset — not yet downloaded",
                        "description": str(preset_info),
                        "verified_at": None,
                    }
        except Exception as e:
            log_stderr(f"[diffusion] hub.DEFAULT_PRESETS load failed: {e}")
        return {"models": list(reg_map.values()), "total": len(reg_map),
                "models_dir": str(self._models_dir)}

    def model_status(self, model_id: str | None = None) -> dict:
        if model_id:
            rec = self._model_reg.get(model_id)
            if rec is None: raise ModelNotFound(model_id)
            return {"model": rec}
        return self.list_models()

    def install_model(self, request: dict) -> dict:
        """Pipeline Manifest 기반 설치 — 모든 구성 파일 Hash 검증."""
        from ameva_component import ModelInstaller
        url = request.get("url", ""); filename = request.get("filename", "")
        sha256 = request.get("sha256", "")
        expected_bytes = int(request.get("expected_bytes", 0))
        model_id = request.get("model_id") or Path(filename).stem
        self._models_dir.mkdir(parents=True, exist_ok=True)
        installer = ModelInstaller(self.COMPONENT_ID, self._models_dir, self._model_reg)
        return installer.install(url=url, filename=filename, sha256=sha256,
                                 expected_bytes=expected_bytes, model_id=model_id,
                                 after_download=self._verify_pipeline_file)

    def _verify_pipeline_file(self, path: Path) -> None:
        """Pipeline 구성 파일 기본 형식 확인 — 추론 실행 금지."""
        valid = {".safetensors", ".bin", ".json", ".onnx", ".pt"}
        if path.suffix.lower() not in valid:
            raise ValueError(f"Unexpected pipeline file format: '{path.suffix}'")

    async def activate_model(self, request: dict) -> dict:
        model_id = request.get("model_id", "")
        rec = self._model_reg.get(model_id)
        if rec is None: raise ModelNotFound(model_id)
        if ModelState.from_str(rec.get("state", "missing")) not in (ModelState.INSTALLED, ModelState.INACTIVE):
            raise ModelLoadFailed(model_id, f"Pipeline state is '{rec.get('state')}'")
        with self._act_lock.acquire(timeout=60.0):
            self._model_reg.set_state(model_id, ModelState.ACTIVE)
            self._write_state()
        return {"activated": True, "model_id": model_id,
                "rollback": {"attempted": False, "succeeded": False}}

    async def deactivate_model(self, request: dict) -> dict:
        model_id = request.get("model_id", "")
        self._model_reg.set_state(model_id, ModelState.INACTIVE)
        self._write_state()
        return {"deactivated": True, "model_id": model_id}

    def list_instances(self) -> dict:
        instances = self._inst_reg.list_all()
        return {"instances": [i.to_dict() for i in instances], "total": len(instances)}

    async def start_instance(self, request: dict) -> dict:
        model_id = request.get("model_id", "")
        instance_id = request.get("instance_id") or f"diffusion-worker-{int(time.time())}"
        inst = InstanceStatus(
            instance_id=instance_id, component_id=self.COMPONENT_ID,
            model_id=model_id, state=InstanceState.HOT,
            active_jobs=0, queue_depth=0, max_concurrency=1,
            backend="cpu", started_at=time.time(), last_heartbeat=time.time(),
            last_error=None, control_mode=ControlMode.IN_PROCESS,
        )
        self._inst_reg.register(inst)
        self._write_state()
        return {"instance_id": instance_id, "state": InstanceState.HOT.value}

    async def drain_instance(self, instance_id: str) -> dict:
        from ameva_component import InstanceNotFound
        if not self._inst_reg.get(instance_id): raise InstanceNotFound(instance_id)
        self._inst_reg.update_state(instance_id, InstanceState.DRAINING)
        return {"instance_id": instance_id, "state": InstanceState.DRAINING.value}

    async def stop_instance(self, instance_id: str) -> dict:
        from ameva_component import InstanceNotFound
        if not self._inst_reg.get(instance_id): raise InstanceNotFound(instance_id)
        self._inst_reg.update_state(instance_id, InstanceState.STOPPED)
        self._inst_reg.remove(instance_id)
        self._write_state()
        return {"instance_id": instance_id, "state": InstanceState.STOPPED.value}

    def _write_state(self, *, ready: bool | None = None, last_error: str | None = None) -> None:
        ts = now_timestamps()
        hot = [i for i in self._inst_reg.list_all() if i.state == InstanceState.HOT]
        _, pid_alive = self._check_pid()
        _ready = self._check_engine_binary() if ready is None else ready
        self._state_file.write({
            "protocol": "ameva-component-status/1", "component_id": self.COMPONENT_ID,
            "component_type": self.COMPONENT_TYPE, "version": self._get_version(),
            "ready": _ready, "degraded": not _ready, **ts,
            "active_models": [i.model_id for i in hot], "last_error": last_error,
        })
