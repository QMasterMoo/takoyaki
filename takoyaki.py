from itertools import combinations, product
from typing import List, Tuple, Callable


class Ingredient():

    def __init__(self, kcal, carb, protein, fat):
        self.kcal = kcal
        self.carb = carb
        self.protein = protein
        self.fat = fat

class Meal():

    def __init__(self):
        self.ingredients = []

    def add_ingredient(self, ingredient: Ingredient):
        self.ingredients.append(ingredient)
        # allow chaining
        return self

    def calculate_stats(self, is_print=False):
        kcal = 0
        carb = 0
        protein = 0
        fat = 0
        for ingredient in self.ingredients:
            kcal += ingredient.kcal
            carb += ingredient.carb
            protein += ingredient.protein
            fat += ingredient.fat

        ingredient_count = len(self.ingredients)
        # kcal /= ingredient_count
        # carb /= ingredient_count
        # protein /=ingredient_count

        base_factor = 100
        scale_factor = kcal / base_factor
        carb /= scale_factor
        protein /= scale_factor
        fat /= scale_factor

        
        results = dict (
            base_factor = base_factor,
            carb_per_bf = carb,
            protein_per_bf = protein,
            fat_per_bf = fat,

            carb_and_protein_per_bf = carb + protein,
            carb_and_fat_per_bf = carb + fat,
            protein_fat_per_bf = protein + fat,

            total_per_bf = carb + protein + fat
        )

        if is_print:
            print(results)
        return results

class AggregationHelper():
    def __init__(self, fn):
        if not fn:
            raise Exception()
        self.fn = fn
        self.value = 0

    def apply_fn(self, test_value):
        # fn expected to have 2 parameters, should genericize later
        self.value = self.fn(self.value, test_value)

def generate_meal_inputs(depth, min_depth = 1):
    meal_inputs = []
    for depth_level in range(min_depth, depth + 1):
        combos = list(combinations(ingredient_map.keys(), depth_level))
        meal_inputs += combos
    return meal_inputs

def build_meals(meal_inputs: List[Tuple]):
    meal_result_map = {}
    for meal_input in meal_inputs:
        meal = Meal()
        for ingredient in meal_input:
            meal.add_ingredient(ingredient_map[ingredient])
        meal_result_map[meal_input] = meal.calculate_stats()

    return meal_result_map

def format_value(value, max_value_length=10):
    if type(value) == float:
        formatted_value = f"{value:>{max_value_length}.2f}"
    elif type(value) == int:
        formatted_value = f"{value:>{max_value_length}}"
    else:
        formatted_value = str(value)
    return formatted_value

ingredient_map = dict(
    octopus =       Ingredient(kcal=224, carb=21.0, protein=4.8, fat=0.3),
    beef =          Ingredient(kcal=263, carb=21.0, protein=3.6, fat=5.9),
    emmental =      Ingredient(kcal=274, carb=21.3, protein=5.3, fat=4.2),
    sausage =       Ingredient(kcal=246, carb=21.3, protein=3.4, fat=4.8),
    cucumber =      Ingredient(kcal=193, carb=24.4, protein=0.3, fat=0.0),
)

if __name__ == '__main__':
    meal_inputs = generate_meal_inputs(5)
    meal_results = build_meals(meal_inputs)

    if len(meal_results) == 0:
        print(f'\tNo Results')
    random_meal_result_for_schema = meal_results[list(meal_results.keys())[0]]
    metric_schema = random_meal_result_for_schema.keys()
    max_metric_len = max([len(metric) for metric in metric_schema])

    metric_agg_map = {}
    for result_key in metric_schema:
        meal_agg_calculations = dict(
            min = AggregationHelper(lambda curr, test: test if test < curr else curr),
            max = AggregationHelper(lambda curr, test: test if test > curr else curr),
            # todo avg, can't run, but can build up somehow?
        )
        metric_agg_map[result_key] = meal_agg_calculations

    for meal, result in meal_results.items():
        sorted_meal = list(meal)
        # why can't I chain with sort??? why doesn't sort return self :(
        sorted_meal.sort()

        
        
        # print meal title
        print(f'{" ".join(sorted_meal)} [{len(sorted_meal)}]:')


        # print metrics for meal, tabbed over
        for metric, value in result.items():
            for agg_name, agg_helper in metric_agg_map[metric].items():
                agg_helper.apply_fn(value)
            print(f'\t{metric:<{max_metric_len + 1}}:{format_value(value)}')

    print ("=====")

    # agg printing
    # TODO - just use af ucking database
    for metric_name, aggs in metric_agg_map.items():
        print(f"{metric_name}")
        for agg_name, agg_helper in aggs.items():
            max_agg_len = 4 # too lazy
            print(f"\t{agg_name:<{max_agg_len + 1}}:{format_value(agg_helper.value)}")
