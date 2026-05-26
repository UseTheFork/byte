from pydantic import BaseModel, Field


class ConstitutionConfig(BaseModel):
    """ """

    enable_ddd: bool = Field(
        default=False,
        description="Enable DDD (Domain Driven Design)",
    )

    enable_dry: bool = Field(
        default=False,
        description="Enable DRY (Don't Repeat Yourself)",
    )

    enable_tdd: bool = Field(
        default=False,
        description="Enable TDD (Test Driven Development)",
    )

    enable_yagni: bool = Field(
        default=False,
        description="Enable YAGNI (You Aren't Gonna Need It)",
    )

    enable_tda: bool = Field(
        default=False,
        description="Enable TDA (Tell, Don't Ask)",
    )
