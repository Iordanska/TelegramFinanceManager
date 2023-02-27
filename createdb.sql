CREATE TABLE budget(
    codename VARCHAR(255) PRIMARY KEY,
    month_limit integer
);

CREATE TABLE  category(
    codename VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    is_base_expense BOOLEAN,
    aliases TEXT
);

CREATE TABLE expense(
    id INTEGER PRIMARY KEY,
    amount INTEGER,
    created DATETIME,
    category_codename VARCHAR(255),
    raw_text TEXT,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

INSERT INTO category (codename, name, is_base_expense, aliases)
values
    ("products", "продукты", True, "еда"),
    ("rent", "квартира", True, "хата, аренда"),
    ("internet", "интернет", True, "инет"),
    ("transport", "транспорт", True, "автобус, метро, проездной, проезд"),
    ("taxi", "такси", False, "яндекс такси"),
    ("cafe", "кафе", False, "кофе, бар"),
    ("sweets", "вкусное", False, "шоколад, конфеты, мороженое"),
    ("cultural", "Культурные мероприятия", False, "театр, выставка, концерт, музей"),
    ("other", "другое", False, "остальное");
