from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from randovania.game.game_enum import RandovaniaGame
from randovania.gui.dialog.select_preset_dialog import SelectPresetDialog


@pytest.mark.parametrize("for_multiworld", [False, True])
def test_select_preset_single_game(skip_qtbot, preset_manager, for_multiworld):
    game = RandovaniaGame.METROID_PRIME_ECHOES
    window_manager = MagicMock()
    window_manager.preset_manager = preset_manager

    options = MagicMock()
    dialog = SelectPresetDialog(window_manager, options, for_multiworld=for_multiworld, allowed_games=[game])
    skip_qtbot.add_widget(dialog)
    assert dialog.select_preset_widget.for_multiworld is for_multiworld

    assert not dialog.accept_button.isEnabled()

    dialog.select_preset_widget.create_preset_tree.select_preset(preset_manager.default_preset_for_game(game))

    assert dialog.accept_button.isEnabled()
    assert dialog.selected_preset == preset_manager.default_preset_for_game(game)


def test_select_preset_two_games_with_name(skip_qtbot, preset_manager):
    game = RandovaniaGame.METROID_PRIME_ECHOES
    window_manager = MagicMock()
    window_manager.preset_manager = preset_manager

    options = MagicMock()
    dialog = SelectPresetDialog(
        window_manager,
        options,
        for_multiworld=True,
        allowed_games=[RandovaniaGame.BLANK, game],
        include_world_name_prompt=True,
    )
    skip_qtbot.add_widget(dialog)

    assert not dialog.accept_button.isEnabled()
    dialog.game_selection_combo.setCurrentIndex(1)

    dialog.select_preset_widget.create_preset_tree.select_preset(preset_manager.default_preset_for_game(game))

    assert not dialog.accept_button.isEnabled()
    assert dialog.selected_preset == preset_manager.default_preset_for_game(game)

    dialog.world_name_edit.setText("The Name")
    dialog.update_accept_button()
    assert dialog.accept_button.isEnabled()
