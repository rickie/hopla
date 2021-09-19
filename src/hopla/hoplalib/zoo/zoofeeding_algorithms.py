"""
A modules with algorithms for feeding multiple pets at once.
"""
from collections import namedtuple
from dataclasses import dataclass
from typing import List

from hopla.hoplalib.zoo.foodmodels import FoodStockpile
from hopla.hoplalib.zoo.petmodels import Pet, Zoo, ZooHelper

FeedPlanItem = namedtuple(typename="FeedPlanItem",
                          field_names=["pet_name", "food_name", "times"])


@dataclass
class ZookeeperFeedPlan:
    """A plan to feed pets.

    This class acts as a wrapper around a list with feeding parameters.
    """

    def __init__(self):
        self.__feed_plan = []

    def add_to_feed_plan(self, pet_name: str, food_name: str, times: int) -> None:
        """Add an item to the zookeeper's feed plan.

        :param pet_name: name of the pet to feed
        :param food_name: name of the food to give
        :param times: number of food items to give
        :return: None
        """
        feed_item = FeedPlanItem(pet_name=pet_name, food_name=food_name, times=times)
        self.__feed_plan.append(feed_item)

    @property
    def feed_plan(self) -> List[FeedPlanItem]:
        """Return the feeding plan.

        :return: The feeding plan. This will be empty when
        no FeedPlanItems have been added yet.
        """
        return self.__feed_plan


@dataclass
class ZooFeedingAlgorithm:
    """
    This class contains an algorithm, when given a zoo and a food stockpile,
    makes a plan to distribute the food over the pets in the zoo.
    """

    def __init__(self, zoo: Zoo, stockpile: FoodStockpile):
        self.__stockpile = stockpile
        self.__zookeeper_plan = ZookeeperFeedPlan()
        self.__zoo: Zoo = ZooHelper(zoo).get_feedable_zoo()

    @property
    def stockpile(self) -> FoodStockpile:
        """Return the stockpile."""
        return self.__stockpile

    @property
    def zookeeper_plan(self) -> ZookeeperFeedPlan:
        """Return the zookeeper plan. Before Making a plan, this will be empty."""
        return self.__zookeeper_plan

    def make_plan(self) -> None:
        """Make the plan.

        This function removes food from the stockpile and adds feeding items
        to the feeding plan.
        """
        helper = ZooHelper(self.__zoo)
        gen1_zoo: Zoo = helper.filter_on_pet(Pet.is_generation1_pet)
        quest_zoo: Zoo = helper.filter_on_pet(Pet.is_quest_pet)
        magic_zoo: Zoo = helper.filter_on_pet(Pet.is_magic_hatching_pet)

        self.__make_plan(gen1_zoo)
        self.__make_plan(quest_zoo)
        self.__make_plan(magic_zoo)

    def __make_plan(self, zoo: Zoo):
        """Make plan for the specified zoo.

        This function assumes that only feedable pets are passed.
        """
        for pet_name, pair in zoo:
            pet: Pet = pair.pet

            if pet.has_just_1_favorite_food():
                food_name = pet.favorite_food()
            else:
                food_name = self.__stockpile.get_most_abundant_food()

            times = pet.required_food_items_until_mount(food_name)
            if self.__stockpile.has_sufficient(food_name, n=times):
                subtract_times = -times
                self.__stockpile.modify_stockpile(food_name,
                                                  n=subtract_times)
                self.__zookeeper_plan.add_to_feed_plan(
                    pet_name=pet_name,
                    food_name=food_name,
                    times=times
                )
