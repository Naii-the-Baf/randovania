from __future__ import annotations

import dataclasses

from randovania.game.game_enum import RandovaniaGame
from randovania.games.prime2.layout.echoes_cosmetic_suits import EchoesSuitPreferences
from randovania.games.prime2.layout.echoes_user_preferences import EchoesUserPreferences
from randovania.layout.base.cosmetic_patches import BaseCosmeticPatches

DEFAULT_HUD_COLOR = (102, 174, 225)


@dataclasses.dataclass(frozen=True)
class EchoesCosmeticPatches(BaseCosmeticPatches):
    disable_hud_popup: bool = True
    speed_up_credits: bool = True
    open_map: bool = True
    unvisited_room_names: bool = True
    pickup_markers: bool = True
    user_preferences: EchoesUserPreferences = dataclasses.field(default_factory=EchoesUserPreferences)
    convert_other_game_assets: bool = False
    use_hud_color: bool = False
    hud_color: tuple[int, int, int] = DEFAULT_HUD_COLOR
    suit_colors: EchoesSuitPreferences = EchoesSuitPreferences()

    @classmethod
    def default(cls) -> EchoesCosmeticPatches:
        return cls()

    @classmethod
    def game(cls) -> RandovaniaGame:
        return RandovaniaGame.METROID_PRIME_ECHOES

    def __post_init__(self) -> None:
        if len(self.hud_color) != 3:
            raise ValueError("HUD color must be a tuple of 3 ints.")
