"""
Code for interacting with a user
"""
import re

import database
import foodblog_parser


class FoodBlog:
    """Class representing a food blog."""

    def __init__(self):
        """Initialize a food blog system and connect to a database."""
        # Get command line arguments
        self.db_filepath, self.ingredients, self.meals = \
            foodblog_parser.get_args()

        # Open the database
        self.connection = database.connect(self.db_filepath)
        database.enable_foreign_keys(self.connection)

        # Create tables
        if self.ingredients is None and self.meals is None:
            for table_type in database.CREATE_TABLE_:
                database.create_table(self.connection, table_type)

    def add_recipes(self):
        """Get recipe info from a user and insert it into a database."""
        print('Pass the empty recipe name to exit.')

        while True:
            recipe_name = input('Recipe name: ')

            if recipe_name == '':
                self.connection.close()
                break
            else:
                recipe_description = input('Recipe description: ')

                values = (recipe_name, recipe_description)
                recipe_id = database.add_entity(
                    self.connection, 'recipes', values)

                # Ask a user when this dish can be served
                self.show_meals()
                mealtimes = input(
                    'Enter proposed meals separated by a space: ').split()

                for mealtime in mealtimes:
                    values = (int(mealtime), recipe_id)
                    database.add_entity(self.connection, 'serve', values)

                # Ask a user about ingredients
                while True:
                    user_input = input(
                        'Input quantity of ingredient <press enter to stop>: ')
                    if user_input == '':
                        break

                    user_input = user_input.split()

                    if len(user_input) == 2:
                        measure_input = ''
                    elif len(user_input) == 3:
                        measure_input = user_input[1]
                    else:
                        raise NotImplementedError

                    quantity_input = user_input[0]
                    ingredient_input = user_input[-1]

                    # Check if measure input is valid
                    if not self.isvalid_measure(measure_input):
                        print('The measure is not conclusive!')
                        continue

                    # Check if ingredient input is valid
                    isvalid_ingredient, matched_ingredient_name = \
                        self.isvalid_ingredient(ingredient_input)
                    if not isvalid_ingredient:
                        print('The ingredient is not conclusive!')
                        continue

                    # Get measure_id from the database
                    selection = database.get_from_table_by_name(
                        self.connection, 'measures', measure_input)
                    measure_id = selection[0][0]

                    # Get ingredient_id from the database
                    selection = database.get_from_table_by_name(
                        self.connection, 'ingredients', matched_ingredient_name)
                    ingredient_id = selection[0][0]

                    # Insert data into the quantity table
                    values = (quantity_input, recipe_id, measure_id, ingredient_id)
                    database.add_entity(self.connection, 'quantity', values)

    def isvalid_measure(self, measure):
        """Check that the measure  is valid."""
        measures = database.get_all_from_table(self.connection, 'measures')
        measures = [name for _, name in measures]

        if measure == '':
            return True

        n_matched_measures = 0
        for measure_name in measures:
            if re.match(measure, measure_name):
                n_matched_measures += 1
            if n_matched_measures > 1:
                return False
        return True

    def isvalid_ingredient(self, ingredient):
        """Check that the ingredient is valid."""
        ingredients = database.get_all_from_table(
            self.connection, 'ingredients')
        ingredients = [name for _, name in ingredients]

        n_matched_ingredients = 0
        for ingredient_name in ingredients:
            if re.search(ingredient, ingredient_name):
                n_matched_ingredients += 1
                matched_ingredient_name = ingredient_name
            if n_matched_ingredients > 1:
                return False, None
        return True, matched_ingredient_name

    def show_meals(self):
        """Print all available meals."""
        meals = database.get_all_from_table(self.connection, 'meals')
        meals_str = [f'{meal_id}) {meal_name}' for meal_id, meal_name in meals]

        print(' '.join(meals_str))

    def select_recipes(self):
        """Return recipes that fulfill selection criteria.

        Return recipes that contain passed all of the passed ingredients
        (recipes may contain other ingredients as well) and can be served at a
        specific mealtime.
        """
        recipes = database.get_recipes_by_criteria(self.connection, self.ingredients, self.meals)

        if recipes:
            print(f'Recipes selected for you: {", ".join(recipes)}')
        else:
            print('There are no such recipes in the database.')

        self.connection.close()


data = {
    "meals": ("breakfast", "brunch", "lunch", "supper"),
    "ingredients":
        ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
    "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")
}

# Create a food blog system
food_blog = FoodBlog()

if food_blog.ingredients is None and food_blog.meals is None:
    # Populate the tables with data
    for item_type in data:
        for value in data[item_type]:
            database.add_entity(food_blog.connection, item_type, (value,))

    food_blog.add_recipes()
else:
    food_blog.select_recipes()
