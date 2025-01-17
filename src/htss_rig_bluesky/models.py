from typing import Literal, Union

from pydantic import BaseModel
from scanspec.specs import Line, Spec, Static

THETA = "theta"
X = "x"
BEAM = "beam"


class Darks(BaseModel):
    num: int

    def to_spec(self) -> Spec:
        return Static(BEAM, 0.0, num=self.num)


class Flats(BaseModel):
    num: int
    out_of_beam: float

    def to_spec(self) -> Spec:
        return Static(BEAM, 1.0, num=self.num).zip(
            Static(X, self.out_of_beam, num=self.num)
        )


class Projections(BaseModel):
    outer_trajectory: Line[Literal[X]] | None = None
    trajectory: Line[Literal[THETA]]

    def to_spec(self) -> Spec:
        if self.outer_trajectory is not None:
            return self.outer_trajectory * self.trajectory
        else:
            return self.trajectory


class TomographySpec(BaseModel):
    operation: Darks | Flats | Projections
    next_stage: Union["TomographySpec", None] = None

    @classmethod
    def default(cls, scale: int = 1) -> "TomographySpec":
        dark_stage = Darks(num=1 * scale)
        flat_stage = Flats(num=1 * scale, out_of_beam=-24.0)
        projection_stage = Projections(
            trajectory=Line(
                axis=THETA,
                start=-180.0,
                stop=180,
                num=5 * scale,
            )
        )
        return cls(
            operation=dark_stage,
            next_stage=cls(
                operation=flat_stage,
                next_stage=cls(
                    operation=projection_stage,
                ),
            ),
        )

    def __iter__(self):
        yield self
        if self.next_stage is not None:
            yield from iter(self.next_stage)
