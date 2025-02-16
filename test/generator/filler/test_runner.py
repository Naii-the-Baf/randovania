from __future__ import annotations

from random import Random
from unittest.mock import MagicMock

from randovania.game_description.db.hint_node import HintNode, HintNodeKind
from randovania.game_description.db.node_identifier import NodeIdentifier
from randovania.game_description.hint import (
    HintItemPrecision,
    HintLocationPrecision,
    LocationHint,
    PrecisionPair,
)
from randovania.game_description.resources.pickup_index import PickupIndex
from randovania.games.prime2.generator.hint_distributor import EchoesHintDistributor
from randovania.generator.filler import runner
from randovania.generator.filler.player_state import HintState
from randovania.generator.generator import create_player_pool


async def test_run_filler(
    blank_game_description,
    blank_game_patches,
    default_blank_configuration,
    mocker,
):
    # Setup
    rng = Random(5000)
    status_update = MagicMock()

    hint_identifiers = [
        node.identifier for node in blank_game_description.region_list.iterate_nodes() if isinstance(node, HintNode)
    ]

    player_pools = [
        await create_player_pool(rng, default_blank_configuration, 0, 1, "World 1", MagicMock()),
    ]
    initial_pickup_count = len(player_pools[0].pickups)

    patches = blank_game_patches.assign_hint(hint_identifiers[0], LocationHint.unassigned(PickupIndex(0)))
    action_log = (MagicMock(), MagicMock())
    player_state = MagicMock()
    player_state.index = 0
    player_state.game = player_pools[0].game
    player_state.pickups_left = list(player_pools[0].pickups)

    filler_config = MagicMock()
    filler_config.minimum_available_locations_for_hint_placement = 0
    player_state.hint_state = HintState(filler_config, blank_game_description)
    empty_set: frozenset[PickupIndex] = frozenset()
    player_state.hint_state.hint_initial_pickups = {identifier: empty_set for identifier in hint_identifiers}

    mocker.patch(
        "randovania.generator.filler.runner.retcon_playthrough_filler",
        autospec=True,
        return_value=({player_state: patches}, action_log),
    )

    # Run
    filler_result = await runner.run_filler(rng, player_pools, ["World 1"], status_update)

    assert filler_result.action_log == action_log
    assert len(filler_result.player_results) == 1
    result_patches = filler_result.player_results[0].patches
    remaining_items = filler_result.player_results[0].unassigned_pickups

    # Assert
    assert len(result_patches.hints) == len(hint_identifiers)
    assert [
        hint for hint in result_patches.hints.values() if isinstance(hint, LocationHint) and hint.precision is None
    ] == []
    assert initial_pickup_count == len(remaining_items) + len(result_patches.pickup_assignment.values())


def test_fill_unassigned_hints_empty_assignment(echoes_game_description, echoes_game_patches):
    # Setup
    rng = Random(5000)
    hint_nodes = [
        node
        for node in echoes_game_description.region_list.iterate_nodes()
        if isinstance(node, HintNode) and node.kind == HintNodeKind.GENERIC
    ]
    hint_distributor = echoes_game_description.game.generator.hint_distributor

    filler_config = MagicMock()
    filler_config.minimum_available_locations_for_hint_placement = 0
    hint_state = HintState(filler_config, echoes_game_description)
    empty_set: frozenset[PickupIndex] = frozenset()
    hint_state.hint_initial_pickups = {node.identifier: empty_set for node in hint_nodes}

    # Run
    result = hint_distributor.fill_unassigned_hints(
        echoes_game_patches,
        echoes_game_description.region_list,
        rng,
        hint_state,
    )

    # Assert
    assert len(result.hints) == len(hint_nodes)


def test_add_hints_precision(empty_patches, blank_pickup):
    player_state = MagicMock()
    player_pools = [MagicMock()]
    rng = MagicMock()
    rng.gauss.return_value = 0.0
    rng.random.return_value = 0.0

    hints = [
        LocationHint(
            PrecisionPair(HintLocationPrecision.DETAILED, HintItemPrecision.DETAILED, include_owner=False),
            PickupIndex(1),
        ),
        LocationHint.unassigned(PickupIndex(2)),
    ]
    pickups = [(PickupIndex(i), blank_pickup) for i in range(1, 4)]
    nc = NodeIdentifier.create

    initial_patches = empty_patches
    for i, hint in enumerate(hints):
        initial_patches = initial_patches.assign_hint(nc("w", "a", f"{i}"), hint)

    initial_patches = initial_patches.assign_own_pickups(pickups)

    hint_distributor = EchoesHintDistributor()

    # Run
    result = hint_distributor.add_hints_precision(player_state, initial_patches, rng, player_pools)

    # Assert
    assert result.hints == {
        nc("w", "a", "0"): LocationHint(
            PrecisionPair(HintLocationPrecision.DETAILED, HintItemPrecision.DETAILED, include_owner=False),
            PickupIndex(1),
        ),
        nc("w", "a", "1"): LocationHint(
            PrecisionPair(HintLocationPrecision.REGION_ONLY, HintItemPrecision.DETAILED, include_owner=True),
            PickupIndex(2),
        ),
    }
