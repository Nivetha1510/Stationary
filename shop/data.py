"""Source data for the `seed_catalogue` management command.

The live site reads everything from the database; this module only describes
the initial catalogue that the command loads.
"""

# ---------------------------------------------------------------- categories

CATEGORIES = [
    {"slug": "office", "title": "Office Basics", "nav": "Office Basics"},
    {"slug": "pens", "title": "Pen & Writings", "nav": "Pen & Writings"},
    {"slug": "paper", "title": "Papers & Notebook", "nav": "Papers & Notebook"},
    {"slug": "school", "title": "School Supplies", "nav": "School Supplies"},
    {"slug": "files", "title": "Files & Folders", "nav": "Files & Folders"},
]

# ------------------------------------------------------------------ products

UNIT_PRICE = 50
OFFER_LINE = "Buy 3 or more @ Rs. 101.20"

# Names follow what each card's image shows (index 1-12 per category).
PRODUCT_NAMES = {
    "office": [
        "Desktop Calculator", "Heavy Duty Stapler", "Desk Organizer Set", "Ballpoint Pen Set",
        "Craft Scissors Set", "Heavy Duty Stapler", "Highlighter Set", "Heavy Duty Stapler",
        "Desk Organizer Set", "Desktop Calculator", "Heavy Duty Stapler", "Desk Organizer Set",
    ],
    "pens": [
        "Ballpoint Pen Set", "Colour Pencil Set", "Spiral Notebook with Pen", "Spiral Notebook with Pen",
        "Spiral Notebook Duo", "Ballpoint Pen Set", "Colour Pencil Set", "Spiral Notebook with Pen",
        "Ballpoint Pen Set", "Ballpoint Pen Set", "Spiral Notebook with Gel Pen", "Colour Pencil Set",
    ],
    "paper": [
        "Ruled Notebook with Markers", "Notebook and Stapler Set", "Drawing Paper with Paint Kit", "Floral Spiral Diary",
        "Ruled Notebook with Markers", "Notebook and Stapler Set", "Floral Spiral Diary", "Drawing Paper with Paint Kit",
        "Ruled Notebook with Markers", "Notebook and Stapler Set", "Drawing Paper with Paint Kit", "Floral Spiral Diary",
    ],
    "school": [
        "Ruler, Pen and Eraser Set", "Pencil Cup with Pencils", "Sticky Notes and Notepad Set", "Sticky Notes and Notepad Set",
        "Spiral Notebook Duo", "Geometry Box Set", "Ruler, Pen and Eraser Set", "Pencil Cup with Pencils",
        "Ballpoint Pen Set", "Pencil Cup with Pencils", "Sticky Notes and Notepad Set", "Ruler, Pen and Eraser Set",
    ],
    "files": [
        "Box File Set", "Lever Arch File Set", "Colourful Lever Arch Files", "Lever Arch File Set",
        "Leather Notebook Set", "Lever Arch File Set", "Colourful Lever Arch Files", "Colourful Lever Arch Files",
        "Leather Notebook Set", "Leather Notebook Set", "Lever Arch File Set", "Colourful Lever Arch Files",
    ],
}


def build_products():
    """12 products per category, matching the 4x3 grid in every Figma frame."""
    products = []
    for category in CATEGORIES:
        slug = category["slug"]
        for index in range(1, 13):
            products.append(
                {
                    "code": f"{slug}-{index}",
                    "name": PRODUCT_NAMES[slug][index - 1],
                    "category": slug,
                    "price": UNIT_PRICE,
                    "offer_text": OFFER_LINE,
                    "rating": 5,
                    "image": f"p-{slug}-{index}.jpg",
                    "display_order": index,
                }
            )
    return products


# Home-page products reuse a catalogue row but carry their own photo and name.
HOME_FEATURED = [
    {"code": "office-1", "image": "prod-calculator.jpg", "name": "Scientific Calculator"},
    {"code": "office-2", "image": "prod-protractor.jpg", "name": "Protractor"},
    {"code": "office-3", "image": "prod-notepad-flat.jpg", "name": "Notepad"},
]

HOME_BACK_TO_SCHOOL = [
    {"code": "school-2", "image": "prod-pencils.jpg", "name": "Pencil"},
    {"code": "paper-1", "image": "prod-notebook-open.jpg", "name": "Ruled Notebook"},
    {"code": "paper-3", "image": "prod-planner.jpg", "name": "Planner"},
]

HOME_TRENDING = [
    "img/trend-1.jpg",
    "img/trend-2.jpg",
    "img/trend-3.jpg",
    "img/trend-4.jpg",
    "img/trend-5.jpg",
    "img/trend-6.jpg",
]

TEAM = [
    {"name": "Seth Rollins", "role": "Shop Owner", "image": "img/team-1.jpg"},
    {"name": "Seth Rollins", "role": "Manager", "image": "img/team-2.jpg"},
    {"name": "Seth Rollins", "role": "Shop Keeper", "image": "img/team-3.jpg"},
]

TESTIMONIAL = {
    "lead_text": "Bulk Stationery. Better Prices. Smarter Supply.",
    "quote": (
        "Working with SupplyHive has been a game-changer for my store. The quality of the "
        "stationery is consistently high, prices are competitive, and orders always arrive "
        "on time—making it easy to keep my shelves stocked and customers happy.\""
    ),
    "author_name": "Priya M",
    "author_role": "Retail shop Owner",
    "avatar": "avatar-priya.jpg",
}
