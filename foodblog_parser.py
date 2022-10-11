"""Script for getting command line arguments."""
import argparse

DEFAULT_DB_FILEPATH = 'database.db'


def set_parser():
    """Return ArgumentParser object with all settings."""
    parser = argparse.ArgumentParser(description='Food blog interface.')

    # Create arguments
    parser.add_argument('db_path', nargs='?', default=DEFAULT_DB_FILEPATH,
                        help='path to the database file (default database.db)')
    parser.add_argument('-i', '--ingredients',
                        required=False,
                        help='list of ingredients separated by commas')
    parser.add_argument('-m', '--meals',
                        required=False,
                        help='list of meals separated by commas')

    return parser


def get_args():
    """Return arguments from command line input."""
    parser = set_parser()
    args = parser.parse_args()

    db_filepath = args.db_path
    ingredients = args.ingredients
    meals = args.meals

    if args.ingredients:
        ingredients = [ingredient.strip() for ingredient in ingredients.split(',')]
    if args.meals:
        meals = [meal.strip() for meal in meals.split(',')]

    return db_filepath, ingredients, meals
