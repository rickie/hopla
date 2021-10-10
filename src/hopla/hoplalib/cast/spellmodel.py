#!/usr/bin/env python3
"""
Module with spell models and data.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

from hopla.hoplalib.errors import YouFoundABugRewardError


class SpellData:
    """A class with data about spells.

    @see: hopla api content | jq .spells
    """
    SpellName = str
    ManaRequired = int
    HabiticaClass = str
    ClassSpellBook = Dict[SpellName, ManaRequired]
    SpellBook = Dict[HabiticaClass, ClassSpellBook]

    warrior_spells_single_arg: ClassSpellBook = {
        "defensiveStance": 25, "valorousPresence": 20, "intimidate": 15
    }
    """@see: hopla api content | jq .spells.warrior"""

    mage_spells_single_arg: ClassSpellBook = {
        "mpheal": 30, "earth": 35
    }
    """@see: hopla api content | jq .spells.wizard"""

    rogue_spells_single_arg: ClassSpellBook = {
        "toolsOfTrade": 25, "stealth": 45
    }
    """@see: hopla api content | jq .spells.rogue"""

    healer_spells_single_arg: ClassSpellBook = {
        "heal": 15, "brightness": 15, "protectAura": 30, "healAll": 25
    }
    """@see: hopla api content | jq .spells.healer"""

    spell_book_single_arg: SpellBook = {
        "warrior": warrior_spells_single_arg,
        "wizard": mage_spells_single_arg,
        "healer": healer_spells_single_arg,
        "rogue": rogue_spells_single_arg
    }

    single_arg_spells: List[SpellName] = (
            list(warrior_spells_single_arg.keys())
            + list(mage_spells_single_arg.keys())
            + list(rogue_spells_single_arg.keys())
            + list(healer_spells_single_arg.keys())
    )
    """Listing of all spell names that don't require a UUID."""


@dataclass
class Spell:
    """A spell."""
    spell_name: str
    target_id: Optional[UUID] = None
    """target_id not supported for now."""

    def __post_init__(self):
        if self.spell_name not in SpellData.single_arg_spells:
            raise YouFoundABugRewardError(f"{self.spell_name=} does not exist.")

    @property
    def mana_required(self) -> int:
        """Return how much mana is needed to cast this spell."""
        return SpellData.spell_book_single_arg[self.class_name][self.spell_name]

    @property
    def class_name(self) -> str:
        """Get the Habitica class from the spell name.

        see: https://habitica.fandom.com/wiki/Class_System
        """
        if self.spell_name in SpellData.warrior_spells_single_arg:
            return "warrior"
        if self.spell_name in SpellData.mage_spells_single_arg:
            return "wizard"
        if self.spell_name in SpellData.healer_spells_single_arg:
            return "healer"
        if self.spell_name in SpellData.rogue_spells_single_arg:
            return "rogue"

        raise YouFoundABugRewardError(f"{self.spell_name=} not implemented yet")
        # Mage: fireball="Burst of Flames", mpheal="Ethereal Surge", earth="Earthquake",
        #         frost="Chilling Frost"
        # Warrior: smash="Brutal Smash", defensiveStance="Defensive Stance",
        #          valorousPresence="Valorous Presence", intimidate="Intimidating Gaze"

        # Rogue: pickPocket="Pickpocket", backStab="Backstab", toolsOfTrade="Tools of the Trade",
        # stealth="Stealth"

        # Healer: heal="Healing Light", protectAura="Protective Aura",
        #          brightness="Searing Brightness",
        #         healAll="Blessing"
        # Transformation Items: snowball="Snowball", spookySparkles="Spooky Sparkles",
        #                       seafoam="Seafoam", shinySeed="Shiny Seed"
