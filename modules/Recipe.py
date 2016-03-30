__author__ = 'ciacicode'
from QuantitativeValue import *


class Recipe(object):
    """Recipe object"""

    def __init__(self, ingredients=[], cook_time=QuantitativeValue(), prep_time=QuantitativeValue(), recipe_yield=QuantitativeValue(), total_time=QuantitativeValue(),recipe_category='', recipe_instructions='', name=''):
        self.name = name
        self.ingredients = ingredients
        self.cookTime = cook_time
        self.prepTime = prep_time
        self.recipeYield = recipe_yield
        self.totalTime = total_time
        self.recipeCategory = recipe_category
        self.recipeInstructions = recipe_instructions

