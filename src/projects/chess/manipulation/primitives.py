from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from projects.chess.robot.safety import SafetyController


@dataclass(frozen=True)
class Pose:
    """Cartesian robot pose used by Phase 1."""

    x: float
    y: float
    z: float

    def as_list(self) -> list[float]:
        return [self.x, self.y, self.z]


class RobotInterface:
    """
    Minimal interface expected by the manipulation primitives.

    The concrete implementation will wrap the LeRobot SO100 interface.
    """

    def move_to(self, position: Sequence[float]) -> None:
        raise NotImplementedError

    def open_gripper(selif) -> None:
        raise NotImplementedError

    def close_gripper(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class ManipulationPrimitives:
    """
    Reusable manipulation primitives for Phase 1.

    These should remain independent from the chess task itself.
    """

    def __init__(
        self,
        robot: RobotInterface,
        safety: SafetyController,
        home: Pose,
        approach_height: float = 0.05,
        grasp_height_offset: float = 0.0,
    ) -> None:
        self.robot = robot
        self.safety = safety

        self.home = home
        self.approach_height = approach_height
        self.grasp_height_offset = grasp_height_offset

    def move_home(self) -> None:
        """Move the robot to its known safe home pose."""
        self._move(self.home)

    def move_to(self, pose: Pose) -> None:
        """Move to a validated Cartesian pose."""
        self._move(pose)

    def move_above(self, position: Sequence[float]) -> None:
        """
        Move above an object while maintaining its X/Y position.
        """
        if len(position) != 3:
            raise ValueError("Position must contain [x, y, z].")

        x, y, z = position

        approach = Pose(
            x=x,
            y=y,
            z=z + self.approach_height,
        )

        self._move(approach)

    def descend_to(self, position: Sequence[float]) -> None:
        """Move down to the object's grasp position."""
        self._move(
            Pose(
                x=position[0],
                y=position[1],
                z=position[2] + self.grasp_height_offset,
            )
        )

    def grasp(self) -> None:
        """Close the gripper."""
        self.robot.close_gripper()

    def release(self) -> None:
        """Open the gripper."""
        self.robot.open_gripper()

    def lift(self, position: Sequence[float]) -> None:
        """Lift vertically above the object."""
        self.move_above(position)

    def pick(self, object_position: Sequence[float]) -> None:
        """
        Execute a complete pick sequence.

        Sequence:

            move above object
            descend
            grasp
            lift
        """
        self.move_above(object_position)
        self.descend_to(object_position)
        self.grasp()
        self.lift(object_position)

    def place(self, target_position: Sequence[float]) -> None:
        """
        Execute a complete place sequence.

        Sequence:

            move above target
            descend
            release
            lift
        """
        self.move_above(target_position)
        self.descend_to(target_position)
        self.release()
        self.lift(target_position)

    def pick_and_place(
        self,
        object_position: Sequence[float],
        target_position: Sequence[float],
    ) -> None:
        """
        Execute the complete Phase 1 pick-and-place task.
        """
        try:
            self.move_home()

            self.pick(object_position)

            self.place(target_position)

            self.move_home()

        except Exception:
            # Put the robot into a known safe state before propagating
            # the error to the experiment runner.
            self.robot.stop()
            raise

    def _move(self, pose: Pose) -> None:
        """Validate and execute a Cartesian move."""
        self.safety.validate_position(pose.as_list())
        self.robot.move_to(pose.as_list())