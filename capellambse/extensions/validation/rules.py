# SPDX-FileCopyrightText: Copyright DB Netz AG and the capellambse contributors
# SPDX-License-Identifier: Apache-2.0

__all__ = ["has_non_empty_description"]

from capellambse.model import common as c
from capellambse.model.layers import la

from . import _validate


@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=la.LogicalComponent,
    id="Rule-001",
    name="No empty description",
    rationale="A LogicalComponent should have a non empty description.",
    actions=["Fill the description text field."],
)
def has_non_empty_description(obj: c.GenericElement) -> bool:
    return bool(obj.description)
