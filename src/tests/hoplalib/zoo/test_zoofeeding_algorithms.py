#!/usr/bin/env python3
from hopla.hoplalib.zoo.zoofeeding_algorithms import FeedPlanItem, ZookeeperFeedPlan


class TestZookeeperFeedPlan:

    def test___init__(self):
        plan = ZookeeperFeedPlan()

        assert plan.feed_plan == []

    def test_add_to_feed_plan(self):
        plan = ZookeeperFeedPlan()
        pet_name = "Axolotl-Zombie"
        food_name = "RottenMeat"
        times = 9
        plan.add_to_feed_plan(pet_name=pet_name,
                              food_name=food_name,
                              times=times)

        expected_plan = [
            FeedPlanItem(pet_name=pet_name, food_name=food_name, times=times)
        ]
        assert plan.feed_plan == expected_plan


class TestZooFeedingAlgorithm:
    print(NotImplementedError("Implement Me!"))
