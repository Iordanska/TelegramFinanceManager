import db


class Category:
    def __init__(self, codename, name, is_base_expense, aliases):
        self.codename = codename
        self.name = name
        self.is_base_expense = is_base_expense
        self.aliases = aliases


class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self):
        categories = db.fetchall(
            "category", ["codename", "name", "is_base_expense", "aliases"]
        )
        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"]
            if aliases:
                aliases = aliases.split(",")
                aliases = list(map(str.strip, aliases))

            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                is_base_expense=category['is_base_expense'],
                aliases=aliases
            ))
        return categories_result

    def get_all_categories(self):
        return self._categories

    def get_category(self, category_name):
        found = None
        other_category = None
        for category in self._categories:

            if category.codename == "other":
                other_category = category

            if category.name == category_name:
                found = category

            if category.aliases:
                for alias in category.aliases:
                    if category_name in alias:
                        found  = category

        if not found:
            found = other_category

        return found
