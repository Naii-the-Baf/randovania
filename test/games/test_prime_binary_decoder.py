from __future__ import annotations

import io
from pathlib import Path

import pytest

import randovania.lib.construct_lib
from randovania import get_data_path
from randovania.game.game_enum import RandovaniaGame
from randovania.game_description import data_reader, game_migration
from randovania.games import binary_data
from randovania.layout.generator_parameters import raw_database_hash

sample_data = {
    "schema_version": game_migration.CURRENT_VERSION,
    "game": "prime2",
    "resource_database": {
        "items": {},
        "energy_tank_item_index": "",
        "events": {},
        "tricks": {},
        "damage": {},
        "versions": {},
        "misc": {},
        "requirement_template": {
            "Foo": {
                "display_name": "Foo",
                "requirement": {"type": "or", "data": {"comment": None, "items": []}},
            }
        },
        "damage_reductions": [],
    },
    "layers": ["default"],
    "starting_location": {"region": "Temple Grounds", "area": "Landing Site", "node": "Save Station"},
    "minimal_logic": None,
    "victory_condition": {
        "type": "and",
        "data": {"comment": None, "items": []},
    },
    "dock_weakness_database": {
        "types": {},
        "default_weakness": {
            "type": "",
            "name": "",
        },
        "dock_rando": {"force_change_two_way": False, "resolver_attempts": 200, "to_shuffle_proportion": 1.0},
    },
    "hint_feature_database": {
        "key": {
            "long_name": "Room",
            "hint_details": ["in ", "a room"],
        },
        "key2": {
            "long_name": "Room",
            "hint_details": ["in ", "a room"],
            "hidden": True,
        },
    },
    "used_trick_levels": {},
    "flatten_to_set_on_patch": False,
    "regions": [],
}


def test_simple_round_trip():
    b = io.BytesIO()
    binary_data.encode(sample_data, b)

    b.seek(0)
    decoded = binary_data.decode(b)

    assert decoded == sample_data


def test_complex_encode(test_files_dir):
    data = test_files_dir.read_json("prime_data_as_json.json")
    data = game_migration.migrate_to_current(data, RandovaniaGame.METROID_PRIME_ECHOES)

    b = io.BytesIO()

    # Run
    binary_data.encode(data, b)
    # # Whenever the file format changes, we can use the following line to force update our test file
    # test_files_dir.joinpath("prime_data_as_binary.bin").write_bytes(b.getvalue()); assert False

    # Assert
    assert test_files_dir.joinpath("prime_data_as_binary.bin").read_bytes() == b.getvalue()


def test_complex_decode(test_files_dir):
    # Run
    decoded_data = binary_data.decode_file_path(Path(test_files_dir.joinpath("prime_data_as_binary.bin")))

    # Assert
    saved_data = test_files_dir.read_json("prime_data_as_json.json")
    saved_data = game_migration.migrate_to_current(saved_data, RandovaniaGame.METROID_PRIME_ECHOES)

    assert decoded_data == saved_data


def _comparable_dict(value):
    if isinstance(value, dict):
        return [(key, _comparable_dict(item)) for key, item in value.items()]

    if isinstance(value, list):
        return [_comparable_dict(item) for item in value]

    return value


def test_full_data_encode_is_equal(game_enum):
    # The json data may be missing if we're running using a Pyinstaller binary
    # Setup
    data_dir = game_enum.data_path.joinpath("logic_database")
    if not data_dir.is_dir() and get_data_path().joinpath("binary_data", f"{game_enum.value}.bin").is_file():
        pytest.skip("Missing json-based data")

    json_database = data_reader.read_split_file(data_dir)
    json_database = game_migration.migrate_to_current(json_database, game_enum)

    b = io.BytesIO()
    binary_data.encode(json_database, b)

    b.seek(0)
    decoded_database = binary_data.decode(b)

    # Run
    assert decoded_database == json_database

    comparable_json = _comparable_dict(json_database)
    comparable_binary = _comparable_dict(decoded_database)
    for a, b in zip(comparable_json, comparable_binary):
        assert a == b

    assert comparable_binary == comparable_json
    assert raw_database_hash(decoded_database) == raw_database_hash(json_database)


reqs_to_test = [
    {"type": "or", "data": {"comment": None, "items": []}},
    {"type": "and", "data": {"comment": None, "items": []}},
    {"type": "or", "data": {"comment": None, "items": []}},
    {"type": "resource", "data": {"type": "items", "name": "Foo", "amount": 7, "negate": True}},
    {"type": "or", "data": {"comment": None, "items": []}},
    {"type": "template", "data": "Example Template"},
]
reqs_to_test.append({"type": "and", "data": {"comment": None, "items": list(reqs_to_test)}})


@pytest.mark.parametrize("req", reqs_to_test)
def test_encode_requirement_simple(req):
    # Run
    encoded = binary_data.ConstructRequirement.build(req)
    decoded = randovania.lib.construct_lib.convert_to_raw_python(binary_data.ConstructRequirement.parse(encoded))

    # Assert
    assert req == decoded


def test_encode_resource_database():
    # Setup
    resource_database = sample_data["resource_database"]

    # Run
    encoded = binary_data.ConstructResourceDatabase.build(resource_database)

    # Assert
    assert encoded == b"\x00\x00\x00\x00\x00\x00\x01\x03Foo\x03Foo\x02\x00\x00\x00\x00"
