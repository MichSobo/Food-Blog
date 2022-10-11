"""
Code for interacting with a database.
"""
import sqlite3
from sqlite3 import Error

CREATE_TABLE_MEALS = '''
CREATE TABLE IF NOT EXISTS meals (
    meal_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    meal_name TEXT NOT NULL UNIQUE
);'''
CREATE_TABLE_INGREDIENTS = '''
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL UNIQUE
);'''
CREATE_TABLE_MEASURES = '''
CREATE TABLE IF NOT EXISTS measures (
    measure_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    measure_name TEXT UNIQUE
);'''
CREATE_TABLE_RECIPES = '''
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id INTEGER NOT NULL PRIMARY KEY,
    recipe_name TEXT NOT NULL,
    recipe_description TEXT
);'''
CREATE_TABLE_SERVE = '''
CREATE TABLE IF NOT EXISTS serve (
    serve_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    meal_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY (meal_id) REFERENCES meals(meal_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
);'''
CREATE_TABLE_QUANTITY = '''
CREATE TABLE IF NOT EXISTS quantity (
    quantity_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    quantity INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    measure_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    CONSTRAINT fk_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipes(recipe_id),
    CONSTRAINT fk_measure FOREIGN KEY (measure_id)
        REFERENCES measures(measure_id),
    CONSTRAINT fk_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(ingredient_id)
);'''
CREATE_TABLE_ = {
    'meals': CREATE_TABLE_MEALS,
    'ingredients': CREATE_TABLE_INGREDIENTS,
    'measures': CREATE_TABLE_MEASURES,
    'recipes': CREATE_TABLE_RECIPES,
    'serve': CREATE_TABLE_SERVE,
    'quantity': CREATE_TABLE_QUANTITY,
}

INSERT_MEAL = 'INSERT INTO meals (meal_name) VALUES (?);'
INSERT_INGREDIENT = 'INSERT INTO ingredients (ingredient_name) VALUES (?);'
INSERT_MEASURE = 'INSERT INTO measures (measure_name) VALUES (?);'
INSERT_RECIPE = 'INSERT INTO recipes (recipe_name, recipe_description) VALUES (?, ?);'
INSERT_SERVE = 'INSERT INTO serve (meal_id, recipe_id) VALUES (?, ?);'
INSERT_QUANTITY = '''
INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id)
VALUES (?, ?, ?, ?)
;'''
INSERT_ = {
    'meals': INSERT_MEAL,
    'ingredients': INSERT_INGREDIENT,
    'measures': INSERT_MEASURE,
    'recipes': INSERT_RECIPE,
    'serve': INSERT_SERVE,
    'quantity': INSERT_QUANTITY,
}

GET_FROM_INGREDIENTS_BY_NAME = 'SELECT * FROM ingredients WHERE ingredient_name = ?;'
GET_FROM_MEASURES_BY_NAME = 'SELECT * FROM measures WHERE measure_name = ?;'
GET_FROM_TABLE_BY_NAME = {
    'measures': GET_FROM_MEASURES_BY_NAME,
    'ingredients': GET_FROM_INGREDIENTS_BY_NAME,
}

GET_ALL_MEALS = 'SELECT * FROM meals;'
GET_ALL_INGREDIENTS = 'SELECT * FROM ingredients;'
GET_ALL_MEASURES = 'SELECT * FROM measures;'
GET_ALL_FROM_TABLE = {
    'meals': GET_ALL_MEALS,
    'ingredients': GET_ALL_INGREDIENTS,
    'measures': GET_ALL_MEASURES,
}

GET_RECIPES_BY_CRITERIA = '''
SELECT r.recipe_id
FROM recipes AS r
INNER JOIN quantity AS q
    ON r.recipe_id = q.recipe_id
    INNER JOIN ingredients AS i
        ON q.ingredient_id = i.ingredient_id
        INNER JOIN serve AS s
            ON r.recipe_id = s.recipe_id
            INNER JOIN meals AS m
                ON s.meal_id = m.meal_id
WHERE
    ingredient_name = "?" AND
    meal_name IN ?
;'''


def connect(db_filepath):
    """Set a database connection to the SQLite database.

    Args:
        db_filepath (str): path to database file

    Returns:
        object: Connection object or None
    """
    try:
        connection = sqlite3.connect(db_filepath)
    except Error as e:
        print(e)
        connection = None

    return connection


def enable_foreign_keys(connection):
    """Enable use of foreign keys in a database."""
    with connection as c:
        c.execute('PRAGMA foreign_keys = ON;')


def create_table(connection, item_type):
    """Create a table of a given item type.

    Args:
        connection (object): sqlite3 Connection object
        item_type (str): one of the item groups from {'meals', 'ingredients',
            'measures', 'recipes', 'serve', 'quantity'}
    """
    with connection as c:
        c.execute(CREATE_TABLE_[item_type])


def add_entity(connection, item_type, values):
    """Add an entity to a table of a given item type.

    Args:
        connection (object): sqlite3 Connection object
        item_type (str): one of the item groups from {'meals', 'ingredients',
            'measures', 'recipes', 'serve', 'quantity}
        values (tuple): values to be added

    Returns:
        int: last inserted row value or None
    """
    with connection as c:
        lastrow_id = c.execute(INSERT_[item_type], values).lastrowid

    return lastrow_id


def get_from_table_by_name(connection, item_type, item_name):
    """Return entities based on their name from a given table."""
    with connection as c:
        return c.execute(GET_FROM_TABLE_BY_NAME[item_type], (item_name, )).fetchall()


def get_all_from_table(connection, item_type):
    """Return all entities from a given table."""
    with connection as c:
        return c.execute(GET_ALL_FROM_TABLE[item_type]).fetchall()


def get_recipes_by_criteria(connection, ingredients, meals):
    """Return recipe names based on ingredient and meal times."""
    result = []
    with connection as c:
        for ingredient in ingredients:
            query = GET_RECIPES_BY_CRITERIA
            query = query.replace('?', ingredient, 1)

            meals_str = '("' + '", "'.join(meals) + '")'
            query = query.replace('?', meals_str, 1)

            recipe_ids = c.execute(query).fetchall()
            recipe_ids = [recipe_id[0] for recipe_id in recipe_ids]

            result.append(recipe_ids)

        recipe_ids_unique = set(result[0]).intersection(*result)

    with connection as c:
        recipe_names = []
        for recipe_id in recipe_ids_unique:
            query = 'SELECT recipe_name FROM recipes WHERE recipe_id = ?'
            recipe_name = c.execute(query, (recipe_id, )).fetchall()[0][0]
            recipe_names.append(recipe_name)

    return recipe_names

