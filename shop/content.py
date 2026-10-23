"""Static site copy that is not stored in the database."""

# Bulk pricing exactly as the cart frame shows: 10+ units cost Rs.249.
UNIT_PRICE = 50
BULK_QTY = 10
BULK_TOTAL = 249

# ------------------------------------------------------- home page sections

HOME_CATEGORY_CARDS = [
    {"image": "img/cat-writing.jpg", "alt": "Writing essentials", "url": "pens"},
    {"image": "img/cat-paper.jpg", "alt": "Paper products", "url": "paper"},
    {"image": "img/cat-folders.jpg", "alt": "Files and folders", "url": "files"},
]

HOME_HIGHLIGHTS = [
    {
        "title": "1. Writing Essentials",
        "body": "From everyday ballpoint pens to premium gel pens and highlighters, our "
        "writing tools ensure clarity, comfort, and reliability. Perfect for "
        "classrooms, offices, or creative spaces, these essentials are built to "
        "support productivity and expression at every level.",
    },
    {
        "title": "2. Paper Products",
        "body": "Whether it’s notebooks, notepads, printer paper, or sticky notes, our paper "
        "supplies cover every need. Designed for durability and smooth "
        "performance, these products are ideal for note-taking, organizing, printing, "
        "or planning in any setting.",
    },
    {
        "title": "3. Classroom & Office Tools",
        "body": "Keep workspaces equipped and efficient with rulers, staplers, scissors, "
        "erasers, and more. These tools bring order and precision to daily tasks, "
        "making them indispensable in both educational and professional "
        "environments.",
    },
]

TEAM_INTRO = (
    "Our team is a dedicated group of professionals passionate about delivering quality "
    "stationery in bulk with efficiency and care. With expertise in sourcing, logistics, "
    "and customer service, we ensure every order meets the highest standards."
)


# ------------------------------------------------------------------- footer

def _link(label, name="about", anchor=""):
    """A footer link: the label plus the URL name (and optional #anchor) it opens."""
    return {"label": label, "name": name, "anchor": anchor}


FOOTER_COLUMNS = [
    {
        "title": "Company",
        "links": [
            _link("About us"),
            _link("Supplyhive corporate"),
            _link("Careers", "contact", "write-us"),
            _link("Team", "about", "team"),
        ],
    },
    {
        "title": "Contact us",
        "links": [
            _link("Help & Support", "contact", "write-us"),
            _link("Partner with us", "contact", "write-us"),
            _link("Ride with us", "contact", "write-us"),
        ],
    },
    {
        "title": "Available in",
        "links": [_link(city) for city in ["Coimbatore", "Bengaluru", "Chennai", "kolkata"]],
    },
    {
        "title": "Legal",
        "links": [_link(label) for label in ["Terms& Conditions", "Cookie policy", "Privacy Policy"]],
    },
]

# ------------------------------------------------------------ order pages

PAYMENT_ICONS = {"cod": "truck", "upi": "upi", "debit": "wallet", "credit": "card"}

# ---------------------------------------------------------- shop price filter

# (value, label, lower bound inclusive, upper bound exclusive; the last range includes its upper bound)
PRICE_RANGES = [
    ("50-100", "Rs. 50-100", 50, 100),
    ("100-200", "Rs. 100-200", 100, 200),
    ("200-300", "Rs. 200-300", 200, 300),
    ("300-500", "Rs. 300-500", 300, 500),
]
