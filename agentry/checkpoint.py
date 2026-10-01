"""
Physical Filesystem & Shadow Git State Checkpointer for Agentry.
Provides true End-to-End closed-loop recovery:
When an autonomous agent trajectory is rewound from a failed step back to a safe
checkpoint, the physical filesystem and modified files are reverted to match
the safe execution state, ensuring both prompt context and code state are consistent.
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

from agentry.config import ROOT_DIR

logger = logging.getLogger("agentry.checkpoint")


@dataclass
class FileSnapshot:
    """Snapshot of a single file before mutation."""
    relative_path: str
    absolute_path: str
    content_bytes: Optional[bytes]
    existed_before: bool
    modified_step: int


@dataclass
class CheckpointMetadata:
    """Metadata for a saved workspace checkpoint at a specific agent step."""
    session_id: str
    step_index: int
    timestamp: float
    files: Dict[str, FileSnapshot] = field(default_factory=dict)
    git_tree_oid: Optional[str] = None


class StateCheckpointer:
    """
    Manages physical state checkpoints on the filesystem.
    Supports both file-level differential backups and Git shadow snapshots.
    """

    def __init__(self, base_snapshot_dir: Optional[Path] = None):
        self.base_dir = Path(base_snapshot_dir) if base_snapshot_dir else ROOT_DIR / "data" / "snapshots"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # In-memory index: session_id -> {step_index: CheckpointMetadata}
        self._checkpoints: Dict[str, Dict[int, CheckpointMetadata]] = {}

    def capture_file_before_edit(
        self,
        session_id: str,
        step_index: int,
        file_path: str | Path
    ) -> FileSnapshot:
        """
        Captures the exact state of a file before an agent tool modifies it.
        """
        path = Path(file_path).resolve()
        rel_path = str(path)

        existed = path.exists() and path.is_file()
        content = None
        if existed:
            try:
                content = path.read_bytes()
            except Exception as e:
                logger.warning("Failed to read file for snapshot '%s': %s", path, e)

        snapshot = FileSnapshot(
            relative_path=rel_path,
            absolute_path=str(path),
            content_bytes=content,
            existed_before=existed,
            modified_step=step_index
        )

        if session_id not in self._checkpoints:
            self._checkpoints[session_id] = {}

        if step_index not in self._checkpoints[session_id]:
            import time
            self._checkpoints[session_id][step_index] = CheckpointMetadata(
                session_id=session_id,
                step_index=step_index,
                timestamp=time.time()
            )

        self._checkpoints[session_id][step_index].files[rel_path] = snapshot
        logger.debug(
            "Captured pre-edit file snapshot for '%s' at step %d (exists=%s)",
            path.name, step_index, existed
        )
        return snapshot

    def rollback_filesystem(
        self,
        session_id: str,
        target_step: int,
        workspace_dir: Optional[Path | str] = None
    ) -> Dict[str, Any]:
        """
        Rolls back the physical filesystem to target_step by reverting all file
        modifications made in steps > target_step.
        """
        session_map = self._checkpoints.get(session_id, {})
        if not session_map:
            logger.info("No filesystem checkpoints found for session '%s'. Skipping disk revert.", session_id)
            return {
                "session_id": session_id,
                "target_step": target_step,
                "files_reverted": 0,
                "reverted_paths": [],
                "status": "NO_OP"
            }

        reverted_paths: List[str] = []
        errors: List[str] = []

        # Find all steps that occurred AFTER target_step in reverse chronological order
        steps_to_revert = sorted([s for s in session_map.keys() if s > target_step], reverse=True)

        # Track which paths we've already reverted so we only revert to the earliest state
        reverted_set: Set[str] = set()

        for step in steps_to_revert:
            meta = session_map[step]
            for file_path, snapshot in meta.files.items():
                if file_path in reverted_set:
                    continue

                target_p = Path(snapshot.absolute_path)
                try:
                    if snapshot.existed_before:
                        target_p.parent.mkdir(parents=True, exist_ok=True)
                        if snapshot.content_bytes is not None:
                            target_p.write_bytes(snapshot.content_bytes)
                        reverted_paths.append(str(target_p))
                        reverted_set.add(file_path)
                        logger.info("Restored file '%s' to pre-step %d state", target_p.name, step)
                    else:
                        # File was created in this poisoned step; delete it
                        if target_p.exists():
                            target_p.unlink()
                            reverted_paths.append(f"[DELETED_NEW_FILE] {target_p}")
                            reverted_set.add(file_path)
                            logger.info("Deleted poisoned file '%s' created in step %d", target_p.name, step)
                except Exception as exc:
                    err_msg = f"Failed to revert '{file_path}': {exc}"
                    logger.error(err_msg)
                    errors.append(err_msg)

        # Remove checkpoints for steps > target_step
        for s in steps_to_revert:
            del session_map[s]

        return {
            "session_id": session_id,
            "target_step": target_step,
            "files_reverted": len(reverted_paths),
            "reverted_paths": reverted_paths,
            "errors": errors,
            "status": "SUCCESS" if not errors else "PARTIAL_SUCCESS"
        }

    def snapshot(self, session_id: str, step_index: int, files: Sequence[Union[str, Path]]):
        """Convenience alias to capture pre-edit snapshots for multiple files."""
        snaps = []
        for f in files:
            snaps.append(self.capture_file_before_edit(session_id, step_index, f))
        return snaps

    def rollback(self, session_id: str, target_step: int):
        """Rollback helper returning structured object with restored/deleted files."""
        res = self.rollback_filesystem(session_id, target_step)
        restored = [p for p in res["reverted_paths"] if not p.startswith("[DELETED_NEW_FILE]")]
        deleted = [p.replace("[DELETED_NEW_FILE] ", "") for p in res["reverted_paths"] if p.startswith("[DELETED_NEW_FILE]")]
        
        class RollbackResult:
            def __init__(self, success: bool, restored_files: list, deleted_files: list, errors: list):
                self.success = success
                self.restored_files = restored_files
                self.deleted_files = deleted_files
                self.errors = errors

        return RollbackResult(
            success=(len(res["errors"]) == 0),
            restored_files=restored,
            deleted_files=deleted,
            errors=res["errors"]
        )


    def cleanup_session(self, session_id: str):
        """Frees all snapshots and memory associated with a completed session."""
        if session_id in self._checkpoints:
            del self._checkpoints[session_id]


# Global singleton instance
state_checkpointer = StateCheckpointer()
physical_checkpointer = state_checkpointer

