# SPDX-FileCopyrightText: Copyright DB Netz AG and the capellambse contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

__all__ = ["has_non_empty_description"]

from capellambse.model import common as c
from capellambse.model.layers import ctx, la

from . import _validate

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.SystemComponent,
    id="SY-001",
    name="System has at least one Function allocated to it.",
    rationale="A System has functionalities and those have to be described.",
    actions=["Allocate at least one Function to the System"],
)
def system_involves_function(sys: ctx.SystemComponent) -> bool:
    return len(sys.allocated_functions) > 0
# TODO: type has to accompanied by a new aoptional attribute called e.g. condition or filter - a Callable[[c.GenericElement], bool] which implements a predicate/expression 
# to postfilter MelodyModel.search() results in cases where not all instances of the type are subject to the rule, e.g. to be able to distinguish between System and an Actor. 
# They both are SystemComponents, but differ just by is_actor value

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.SystemFunction,
    id="SF-030",
    name="A System Function shall be allocated to either a System or a System Actor.",
    rationale="An unallocated System Function would be useless because it would not be implemented within any component.",
    actions=["Allocate or delete the Function."],
)
def function_is_allocated(func: ctx.SystemFunction) -> bool:
    return bool(func.owner)

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=fa.Function,
    id="SF-040",
    name="A Function shall have at least one input or output.",
    rationale="A Function wit neither any inputs nor outputs would be useless because it would not interact with any other function of the model.",
    actions=["Add an Function Input Port or a Function Output Port to the Function or delete the Function."],
)
def function_has_inputs_and_outputs(func: fa.Function) -> bool:
    return len(func.inputs) > 0 or len(func.outputs) > 0 # len is more explicit than "return func.inputs and func.outputs"

@_validate.register_rule(
    category=_validate.Category.RECOMMENDED,
    type=ctx.SystemFunction,
    id="SF-050",
    name="A System Function shall be connected to at least one System Actor through a Functional Exchange.",
    rationale="A System Function is justified only if it provides some useful service directly to an System Actor. BUT: there are functions connected only to other functions, \
    which then connect to actors. So the rule should read: A System Function shall be connected directly or indirectly (via other functions) to at least one System Actor through a Functional Exchange.",
    actions=["Connect the System Function via a Functional Exchange to a System Actor or to another System Function which is (directly or indirectly) connected \
    to a System Actor or delete the System Function."],
)
def function_of_system_exchanges_with_actor(func: ctx.SystemFunction) -> bool:
    using_actors = sum(ex.source.is_actor or ex.target.is_actor for ex in func.related_exchanges)
    return bool(using_actors)
# TODO: the above mentioned .condition/.filter attribute is needed here too, 
# to constrain this rule to just functions allcoated to the system (and exclude those allocated to the actors)

@_validate.register_rule(
    category=_validate.Category.SUGGESTED,
    type=fa.FunctionalExchange,
    id="SFE-020",
    name="At least one allocated Exchange Item shall be transmitted over a Functional Exchange.",
    rationale="Depending on the level of detail of the model, a Functional Exchange not using any Exchange Itema may be incomplete.",
    actions=["Add an Exchange Item to the Functional Exchange."],
)
def exchange_transmits_items(ex: fa.FunctionalExchange) -> bool:
    return len(ex.exchange_items) > 0 

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="SC-200",
    name="System Capability represents a behaviour",
    rationale="A System Capability needs to be substantiated and concretized by specification of an actual behaviour (a use case) in adequate level of detail.",
    actions=["Specify the behaviour of the System Capability by performing ARCH.052 Create initial system exchange scenarios or ARCH.053 Create initial system functional chains"],
)
def capability_involves_functional_chain_or_scenario(cap: ctx.Capability) -> bool:
    return len(cap.involved_chains) > 0 or len(cap.scenarios) > 0

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=la.LogicalComponent,
    id="Rule-001",
    name="No empty description",
    rationale="An object shall have a description or summary.",
    actions=["Fill the description text field."],
)
def has_non_empty_description(obj: c.GenericElement) -> bool:
    return bool(obj.description)

@_validate.register_rule(
    category=_validate.Category.RECOMMENDED,
    type=la.LogicalComponent,
    id="Rule-001",
    name="No empty summary",
    rationale="An object shall have a description or summary.",
    actions=["Fill the summary text field."],
)
def has_non_empty_summary(obj: c.GenericElement) -> bool:
    return bool(obj.summary)

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="Rule-002",
    name="Capability involves an Actor",
    rationale="Every Capability shall involve an Actor",
    actions=["Add an involvement with an actor to the Capability."],
)
def capability_involves_an_actor(cap: ctx.Capability) -> bool:
    return len(cap.involved_components.by_is_actor(True)) > 0

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="Rule-003",
    name="Capability involves an actor function",
    rationale="Every Capability shall have an involvement to an actor function.",
    actions=["Add an involvement with an actor function to the Capability."],
)
def capability_involves_an_actor_function(cap: ctx.Capability) -> bool:
    actor_owners = [
        True
        for fnc in cap.involved_functions
        if (fnc.owner and fnc.owner.is_actor)
    ]
    return len(actor_owners) > 0

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="Rule-004",
    name="Capability involves a SystemFunction",
    rationale="Every Capability shall have an involvement to a SystemFunction.",
    actions=["Add an involvement with a SystemFunction to the Capability."],
)
def capability_involves_a_system_function(cap: ctx.Capability) -> bool:
    system_owners = [
        True
        for fnc in cap.involved_functions
        if (fnc.owner and not fnc.owner.is_actor)
    ]
    return len(system_owners) > 0

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="Rule-005",
    name="IS- and SHOULD-entity-involvements match",
    rationale="This should be a thing.",
    actions=["Make more involvements."],
)
def is_and_should_entity_involvements_match(cap: ctx.Capability) -> bool:
    is_involvements = {x.owner.uuid for x in cap.involved_functions if x.owner}
    should_involvements = {x.uuid for x in cap.involved_components}
    return is_involvements == should_involvements

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="Rule-006",
    name="Capability has precondition",
    rationale="A Capability shall define its precondition.",
    actions=["Fill in the precondition of the Capability."],
)
def has_precondition(cap) -> bool:
    return cap.precondition is not None

@_validate.register_rule(
    category=_validate.Category.REQUIRED,
    type=ctx.Capability,
    id="Rule-007",
    name="Capability has postcondition",
    rationale="A Capability shall define its postcondition.",
    actions=["Fill in the postcondition of the Capability."],
)
def has_postcondition(cap):
    return cap.postcondition is not None

try:
    import spacy
except ImportError:

    @_validate.register_rule(
        category=_validate.Category.SUGGESTED,
        type=ctx.Capability,
        id="Rule-007",
        name="Spacy failed to load",
        rationale="Cannot apply this rule.",
        actions=["Install spacy and download the natural language model."],
    )
    def behavior_name_follows_verb_noun_pattern(obj) -> bool:
        del obj
        return False

else:
    NLP = spacy.load("en_core_web_lg")

    @_validate.register_rule(
        category=_validate.Category.REQUIRED,
        type=ctx.Capability,
        id="SC-106",
        name="Behavior name follows verb-noun pattern",
        rationale="This makes things more consistent.",
        actions=[
            'Change the name of the behavior to follow the pattern of "VERB NOUN",'
            ' for example "brew coffee".'
        ],
    )
    @_validate.register_rule(
        category=_validate.Category.RECOMMENDED,
        type=ctx.SystemFunction,
        id="SF-010",
        name="Behavior name follows verb-noun pattern",
        rationale="This makes things more consistent.",
        actions=[
            'Change the name of the behavior to follow the pattern of "VERB NOUN",'
            ' for example "brew coffee".'
        ],
    )
    def behavior_name_follows_verb_noun_pattern(obj) -> bool:
        if len(obj.name) < 1:
            return False
        doc = NLP(obj.name)
        if len(doc) < 2:
            return False
        if doc[0].pos_ != "VERB":
            return False
        if not "NOUN" in [x.pos_ for x in doc[1:]]:
            return False
        return True
