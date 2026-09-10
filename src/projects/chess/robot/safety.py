from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class WorkspaceLimits:
    """Cartesian workspace limits in meters."""

    x_min: float
    x_max: float

    y_min: float
    y_max: float

    z_min: float
    z_max: float

    def contains(self, position: Sequence[float]) -> bool:
        """Return True if an XYZ position is inside the allowed workspace."""
        if len(position) != 3:
            raise ValueError("Position must contain exactly 3 values: [x, y, z].")

        x, y, z = position

        return (
            self.x_min <= x <= self.x_max
            and self.y_min <= y <= self.y_max
            and self.z_min <= z <= self.z_max
        )


class SafetyViolation(RuntimeError):
    """Raised when a requested robot action violates a safety constraint."""


class SafetyController:
    """
    Safety checks for Phase 1 manipulation.

    This class does not directly control the robot. It validates commands
    before they are passed to the robot interface.
    """

    def __init__(
        self,
        workspace: WorkspaceLimits,
        max_gripper_opening: float = 1.0,
    ) -> None:
        self.workspace = workspace
        self.max_gripper_opening = max_gripper_opening

    def validate_position(self, position: Sequence[float]) -> None:
        """Validate an XYZ Cartesian position."""
        if not self.workspace.contains(position):
            raise SafetyViolation(
                f"Requested position {list(position)} is outside "
                f"the allowed workspace: {self.workspace}"
            )

    def validate_gripper(self, opening: float) -> None:
        """Validate gripper command."""
        if not 0.0 <= opening <= self.max_gripper_opening:
            raise SafetyViolation(
                f"Invalid gripper command: {opening}. "
                f"Expected [0, {self.max_gripper_opening}]."
            )

    def validate_trajectory(
        self,
        positions: Sequence[Sequence[float]],
    ) -> None:
        """Validate every Cartesian point in a trajectory."""
        for index, position in enumerate(positions):
            try:
                self.validate_position(position)
            except SafetyViolation as exc:
                raise SafetyViolation(
                    f"Unsafe trajectory point at index {index}: {exc}"
                ) from exc