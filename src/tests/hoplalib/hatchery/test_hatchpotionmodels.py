#!/usr/bin/env python3
import random

import click
import pytest

from hopla.hoplalib.errors import YouFoundABugRewardError
from hopla.hoplalib.hatchery.hatchdata import HatchPotionData
from hopla.hoplalib.hatchery.hatchpotionmodels import HatchPotion, HatchPotionCollection, \
    HatchPotionException

_SAMPLE_SIZE = 10


class TestHatchPotion:
    def test__init__invalid_name_fail(self):
        name = "InvalidName"
        with pytest.raises(HatchPotionException) as exec_info:
            HatchPotion(name, quantity=1)

        assert str(exec_info.value).startswith(f"{name} is not a valid hatching potion name.")
        assert exec_info.errisinstance((YouFoundABugRewardError, click.ClickException))

    @pytest.mark.parametrize(
        "potion_name,quantity",
        list(zip(random.sample(HatchPotionData.hatch_potion_names, k=_SAMPLE_SIZE),
                 range(-_SAMPLE_SIZE, 0)))
    )
    def test__init__invalid_quantity_fail(self, potion_name: str, quantity: int):
        with pytest.raises(HatchPotionException) as exec_info:
            HatchPotion(potion_name, quantity=quantity)

        assert str(exec_info.value).startswith(f"{quantity} is below 0.")
        assert exec_info.errisinstance((YouFoundABugRewardError, click.ClickException))

    @pytest.mark.parametrize(
        "potion_name,quantity",
        list(zip(random.sample(HatchPotionData.hatch_potion_names, k=_SAMPLE_SIZE),
                 range(0, _SAMPLE_SIZE)))
    )
    def test__repr__ok(self, potion_name: str, quantity: int):
        potion = HatchPotion(potion_name, quantity=quantity)

        result: str = repr(potion)

        assert result == f"HatchPotion({potion_name}: {quantity})"

    @pytest.mark.parametrize("potion_name,quantity", [
        ("Base", 10),
        ("CottonCandyBlue", 1),
        ("Golden", 0),
    ])
    def test_is_standard_potion(self, potion_name: str, quantity: int):
        potion = HatchPotion(potion_name, quantity=quantity)

        assert potion.is_standard_hatch_potion() is True
        assert potion.is_magic_hatch_potion() is False
        assert potion.is_wacky_hatch_potion() is False

    @pytest.mark.parametrize("potion_name,quantity", [
        ("BirchBark", 10),
        ("Windup", 1),
        ("Vampire", 0),
        ("Ruby", 9),
        ("Amber", 69),
        ("MossyStone", 42),
        ("SolarSystem", 9001),
    ])
    def test_is_magic_potion(self, potion_name: str, quantity: int):
        potion = HatchPotion(potion_name, quantity=quantity)

        assert potion.is_standard_hatch_potion() is False
        assert potion.is_magic_hatch_potion() is True
        assert potion.is_wacky_hatch_potion() is False

    @pytest.mark.parametrize("potion_name,quantity", [
        ("Veggie", 10),
        ("Dessert", 0),
    ])
    def test_is_wacky_hatch_potion(self, potion_name: str, quantity: int):
        potion = HatchPotion(potion_name, quantity=quantity)

        assert potion.is_standard_hatch_potion() is False
        assert potion.is_magic_hatch_potion() is False
        assert potion.is_wacky_hatch_potion() is True


class TestHatchPotionCollection:
    def test__init__empty_ok(self):
        collection = HatchPotionCollection()
        assert collection == HatchPotionCollection({})
        assert len(collection) == 0

    def test__init__ok(self):
        potion_dict = {"Base": 0, "Moonglow": 42, "Sunset": 2}

        collection = HatchPotionCollection(potion_dict)

        assert collection["Base"] == HatchPotion("Base", quantity=0)
        assert collection["Moonglow"] == HatchPotion("Moonglow", quantity=42)
        assert collection["Sunset"] == HatchPotion("Sunset", quantity=2)

    def test__iter__ok(self):
        collection = HatchPotionCollection({"Base": 1, "Moonglow": 42, "Sunset": 2})

        iterator = iter(collection)

        assert next(iterator) == "Base"
        assert next(iterator) == "Moonglow"
        assert next(iterator) == "Sunset"
        with pytest.raises(StopIteration):
            next(iterator)

    def test__getitem__ok(self):
        collection = HatchPotionCollection({"Base": 1, "Moonglow": 42, "Sunset": 0})

        assert collection["Base"] == HatchPotion("Base", quantity=1)
        assert collection["Moonglow"] == HatchPotion("Moonglow", quantity=42)
        assert collection["Sunset"] == HatchPotion("Sunset", quantity=0)

    def test_remove_hatch_potion_ok(self):
        potion1_quantity = 3
        potion2_quantity = 42
        potion3_name, potion3_quantity = "Sunset", 1
        collection = HatchPotionCollection({
            "Base": potion1_quantity,
            "Moonglow": potion2_quantity,
            potion3_name: potion3_quantity
        })

        collection.remove_hatch_potion(HatchPotion("Base"))
        collection.remove_hatch_potion(HatchPotion("Moonglow"))
        collection.remove_hatch_potion(HatchPotion(potion3_name))

        assert collection["Base"] == HatchPotion("Base",
                                                 quantity=potion1_quantity - 1)
        assert collection["Moonglow"] == HatchPotion("Moonglow",
                                                     quantity=potion2_quantity - 1)
        assert collection[potion3_name] == HatchPotion(potion3_name,
                                                       quantity=potion3_quantity - 1)

    def test_remove_hatch_potion_not_available_faile(self):
        collection = HatchPotionCollection({"Base": 1})

        not_found_potion_name = "Moonglow"
        with pytest.raises(HatchPotionException) as exec_info:
            collection.remove_hatch_potion(HatchPotion(not_found_potion_name))

        expected_msg = f"{not_found_potion_name} was not in the collection "
        assert str(exec_info.value).startswith(expected_msg)
