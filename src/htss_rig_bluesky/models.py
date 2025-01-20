from typing import Literal

import numpy as np
from pydantic import BaseModel
from scanspec.specs import Line, Spec, Static

THETA = "theta"
X = "x"
BEAM = "beam"


class Darks(BaseModel):
    num: int
    stream_name: Literal["darks"] = "darks"

    def as_scanspec(self) -> Spec:
        return Static(BEAM, 0.0, num=self.num)


class Flats(BaseModel):
    num: int
    out_of_beam: float
    stream_name: Literal["flats"] = "flats"

    def as_scanspec(self) -> Spec:
        return Static(BEAM, 1.0, num=self.num).zip(
            Static(X, self.out_of_beam, num=self.num)
        )


class Projections(BaseModel):
    trajectory: Spec[Literal[THETA, X]]
    stream_name: Literal["projections"] = "projections"

    def as_scanspec(self) -> Spec:
        return self.trajectory


Operation = Darks | Flats | Projections


class TomographySpec(BaseModel):
    sample_operations: list[Operation]

    @classmethod
    def default(
        cls,
        resolution: float = 1.0,
        dark_percent: float = 0.2,
        flat_percent: float = 0.2,
        correction_interval_percent: float = 0.2,
    ) -> "TomographySpec":
        num_projections = np.ceil(180.0 / resolution)
        num_darks_per_correction = np.ceil(num_projections * dark_percent)
        num_flats_per_correction = np.ceil(num_projections * flat_percent)

        dark_stage = Darks(num=num_darks_per_correction)
        flat_stage = Flats(num=num_flats_per_correction, out_of_beam=-24.0)

        interval = int(np.floor(1 / correction_interval_percent))
        chunks = [range(i, i + interval - 1) for i in range(-180, 180, interval)]

        operations: list[Operation] = []

        for chunk in chunks:
            operations.append(dark_stage)
            operations.append(flat_stage)
            operations.append(
                Projections(
                    trajectory=Line(
                        axis=THETA,
                        start=chunk.start,
                        stop=chunk.stop,
                        num=len(chunk),
                    )
                )
            )

        return cls(sample_operations=operations)
