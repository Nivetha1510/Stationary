# Supplyhive — Stationery Shop Website Layout

A pixel-accurate, fully responsive Django replication of the **Stationery Shop Website
Layout** Figma prototype.

| | |
|---|---|
| **Stack** | Python 3, Django 5.2, HTML5, CSS3, vanilla JavaScript |
| **Font** | Roboto (self-hosted, bundled — no CDN required) |
| **Primary** | `#097AFA` |
| **Secondary** | `#7AABF5` |
| **Light accent / page background** | `#D3DFF8` |
| **Submission** | 22 October 2026 |

---

## 1. Quick start

```bash
# 1. create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run
python manage.py migrate          # creates the session table
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

No API keys, no `.env` file and no internet connection are needed — the fonts and all
image assets are bundled in `static/`.

---

## 2. Pages

Every frame in the prototype is implemented as its own route.

| Page | URL | Template |
|---|---|---|
| Home | `/` | `pages/home.html` |
| Shop — Office Basics | `/shop/` | `pages/category.html` |
| Pen & Writings | `/category/pens/` | `pages/category.html` |
| Papers & Notebook | `/category/paper/` | `pages/category.html` |
| School Supplies | `/category/school/` | `pages/category.html` |
| Files & Folders | `/category/files/` | `pages/category.html` |
| About us | `/about/` | `pages/about.html` |
| Contact | `/contact/` | `pages/contact.html` |
| Login / Register (Signin) | `/login/` | `pages/signin.html` |
| My Cart | `/cart/` | `pages/cart.html` |
| Billing Details | `/billing/` | `pages/billing.html` |
| My Order | `/orders/` | `pages/my_order.html` |
| Order Tracking | `/tracking/` | `pages/tracking.html` |
| Search results | `/search/?q=` | `pages/search.html` |

---

## 3. Project structure

```
stationery_shop/
├── manage.py
├── requirements.txt
├── README.md
├── config/                     # project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── shop/                       # the application
│   ├── urls.py                 # all routes
│   ├── views.py                # page + cart views
│   ├── models.py               # catalogue, content, customer and order models
│   ├── forms.py                # register, login, contact and billing forms
│   ├── signals.py              # creates a Customer profile for every new user
│   ├── admin.py                # configured admin panel
│   ├── content.py              # static site copy (footer, highlights, sample order)
│   ├── data.py                 # source data for the seed_catalogue command
│   ├── management/commands/    # seed_catalogue
│   ├── cart.py                 # session-backed cart service
│   └── context_processors.py   # cart badge + footer on every page
├── templates/
│   ├── base.html               # nav, footer, flash messages
│   ├── partials/
│   │   ├── icons.html          # inline SVG icon set
│   │   └── product_card.html   # reusable product card
│   └── pages/                  # one template per screen
├── media/                      # uploaded/seeded product, team and trending images
└── static/
    ├── css/fonts.css           # @font-face for the bundled Roboto
    ├── css/style.css           # design tokens + all page styling
    ├── js/main.js              # nav, categories panel, cart, add-to-cart
    ├── fonts/                  # Roboto 300/400/500/700/900 + Roboto Slab 700
    └── img/                    # all design image assets
```

### Template inheritance

Every page extends `base.html`, which holds the sticky navigation bar, the five-column
footer, the app-download band and the flash-message area. Repeated UI is factored into
`partials/` — the product card is a single include used by the home page, all five
category pages and the search results.

---

## 4. Design system

All tokens live at the top of `static/css/style.css` as CSS custom properties, so the
palette and type scale are changed in one place:

```css
--blue:      #097afa;   /* buttons, active nav link, search pill, contact tiles */
--blue-soft: #7aabf5;   /* product-card surface, form inputs, order total */
--blue-pale: #d3dff8;   /* page background */
--star:      #fae823;   /* product rating stars */
```

Layout constants (`--container: 1312px`, `--nav-h: 76px`, radii, card shadow) are tokens
too. Measurements — container width, card size (313 px), grid gutters (97 px), section
rhythm and type sizes — were taken directly off the 1440 px Figma artboard; the rendered
page lands within ~30 px of the prototype across its full 6 241 px height.

---

## 5. Responsive behaviour

| Breakpoint | Behaviour |
|---|---|
| **≥ 1201 px** | Desktop — exact Figma layout. The home hero keeps its free-form absolute composition. |
| **1024 – 1200 px** | Hero reflows to a grid; decorative artwork is hidden; grid gutters tighten. |
| **≤ 1024 px (tablet)** | Nav collapses to a hamburger, search moves to its own row; all grids drop to 2 columns; billing becomes a single column. |
| **≤ 680 px (mobile)** | Single-column everywhere; the cart table becomes stacked cards with `data-label` prefixes; type scale steps down. |

Verified with no horizontal overflow at 1440 / 1024 / 768 / 390 px.

---

## 6. Functionality

- **Add to cart** — posts via `fetch` and updates the nav badge without a page reload;
  falls back to a normal form POST if JavaScript is unavailable.
- **Cart** — session-backed. `+` / `−` buttons and the quantity field all update the
  line, and bulk pricing applies exactly as the prototype shows (10 or more → Rs. 249).
- **Checkout** — Cart → Billing Details → *Place order* → My Order → Order Tracking.
  The order is stored in the session and the cart is cleared.
- **Categories panel** — the ☰ *Categories* control on every category page opens an
  animated panel linking all five categories.
- **Search** — the nav search bar queries the catalogue and renders a results grid.
- **Forms** — the contact and sign-in forms POST, are CSRF-protected, use HTML5
  validation and return a confirmation message.

---

## 7. Accessibility & code quality

- Semantic landmarks (`header`, `nav`, `main`, `footer`, `article`, `ol`), a skip link,
  and visible focus rings.
- Every icon is inline SVG marked `aria-hidden`; every control has an accessible name.
- Images carry descriptive `alt` text; decorative artwork uses empty `alt`.
- `prefers-reduced-motion` disables all transitions.
- CSS is organised token → reset → layout → component → responsive, with reusable
  classes (`.card`, `.btn`, `.field`, `.form-card`, `.order-box`) rather than one-off
  rules. JavaScript is a single IIFE in strict mode with no dependencies.

---

## 8. Testing checklist

| Check | Result |
|---|---|
| All 14 routes return HTTP 200 | ✅ |
| `python manage.py check` | ✅ no issues |
| Every image asset resolves | ✅ |
| Add to cart → badge updates | ✅ |
| Quantity `+` / `−` / direct entry | ✅ |
| Bulk price (10 → Rs. 249) | ✅ |
| Checkout → order → tracking | ✅ |
| Cart cleared after placing order | ✅ |
| Contact form submit + confirmation | ✅ |
| Sign-in form submit | ✅ |
| Search returns results | ✅ |
| Categories panel toggles | ✅ |
| Mobile hamburger toggles | ✅ |
| No horizontal overflow @ 1440/1024/768/390 | ✅ |
| No JavaScript console errors | ✅ |
| Roboto loads (400/700/Slab 700) | ✅ |
| Side-by-side vs Figma, all 13 frames | ✅ |

---

## 9. Notes on the source design

Two points where the prototype is internally inconsistent, and how they were handled:

1. **Result count.** Every category frame draws a **4 × 3 grid of 12 product cards**
   while the caption above reads *"Showing Result 1-9 of 9 results"*. The visual grid was
   treated as authoritative (12 cards), and the caption is now computed from the actual
   product count, so it stays correct if the catalogue changes.

2. **Image assets.** The Google Drive asset link in the brief was not reachable, so every
   photograph, icon, logo and store badge was extracted at full resolution from the
   supplied 1440 px design frames. No placeholder or substitute imagery is used anywhere.

Product copy (*"Scientific Calculator"*, *"Rs. 50"*, *"Buy 3 or more @ Rs. 101.20"*,
5-star ratings) is reproduced verbatim from the prototype, including where the prototype
repeats the same label across differing product images.

## 10. Models & Admin

The catalogue, home-page content, contact messages and orders live in the database
(`shop/models.py`); the pages read them through the ORM.

| Model | Purpose | Key fields |
|-------|---------|-----------|
| `Category` | Shop categories / nav entries | `slug` (unique), `title`, `nav_title`, `display_order` |
| `Product` | Catalogue item | `code` (unique, e.g. `office-1`, used as the cart key), `name`, `category` (FK, PROTECT), `price`, `offer_text` (`offer_line`), `rating` 1-5, `image`, `is_featured`, `is_back_to_school`, `display_order` |
| `TrendingImage` | Home "Trending" grid | `image`, `caption`, `display_order` |
| `TeamMember` | About / home team cards | `name`, `role`, `photo`, `display_order` |
| `Testimonial` | Home testimonial (first active one is shown) | `lead_text`, `quote`, `author_name`, `author_role`, `avatar`, `is_active` |
| `ContactMessage` | Saved from the contact form | `name`, `email`, `phone`, `message`, `created_at`, `is_handled` |
| `Order` | Placed at checkout | `order_code` (auto, `OD` + 9 digits), customer/address fields, `payment_method`, `status`, `total`; `timeline()` returns the four tracking steps |
| `OrderItem` | Order lines | `order` (FK, CASCADE), `product` (FK, PROTECT), `quantity`, `unit_price`, `line_total` |

Order `status` (confirmed, shipped, out for delivery, delivered) drives the tracking
page timeline. Images are stored under `media/` (`MEDIA_URL = "media/"`, served by
Django while `DEBUG` is on), so Pillow is required.

### Setting up the data

```bash
python manage.py migrate
python manage.py seed_catalogue       # idempotent: 5 categories, 60 products,
                                      # 6 trending images, 3 team members, 1 testimonial
python manage.py createsuperuser      # then sign in at /admin/
```

`seed_catalogue` is safe to run repeatedly (it uses `update_or_create`) but it resets
the seeded products, so re-running it overwrites admin edits to those rows.
The six home-page products (`office-1/2/3`, `school-2`, `paper-1/3`) carry their own
photo and name, which also appear on their category cards.

### Admin panel

`/admin/` (header "Supplyhive Administration") lists every model. Products can be edited
in the list (price, featured, back-to-school); orders have an inline items table,
filters, date drill-down and bulk actions to mark orders shipped / out for delivery /
delivered; contact messages have a "mark as handled" action.

## 11. Authentication

Customers register and sign in with **email + password** on `/login/` (one card with
"Sign in" and "Register" tabs). Django's built-in `User` is used with `username` set to the
lower-cased email, and `first_name` holding the display name. Every new user gets a
`Customer` profile (phone number) through a `post_save` signal.

- **Registration** (`RegisterForm`): name, email, phone (10-15 digits, spaces/hyphens
  stripped) and password. The password goes through Django's `AUTH_PASSWORD_VALIDATORS`,
  a duplicate email is a field error, and the new user is signed in immediately.
- **Login** (`LoginForm`): a wrong password and an unknown email give the same message,
  "Email or password is incorrect.", so the form never reveals whether an account exists.
  Admin accounts created with a plain username sign in at `/admin/`, not on this form.
- **Password hashing:** passwords are stored with `set_password()` (PBKDF2-SHA256,
  `pbkdf2_sha256$...`); the plain text is never saved.
- **Sessions:** cookie lifetime is 14 days, refreshed on every request. `login()` rotates
  the session key. Logout is a POST (`/logout/`) from the nav button.
- **Protected pages:** `/billing/`, `/orders/` and `/tracking/` require sign-in and redirect
  to `/login/?next=...`; after login the user returns to the page they asked for (only
  same-site `next` values are followed). Orders are filtered by `Order.user`, so a customer
  only ever sees their own; orders created before accounts existed have no owner and are
  visible only in the admin.
- **Cart across login:** the cart lives in the session and Django keeps session data when it
  rotates the key at login, so a guest's cart is still there after signing in or
  registering. Signing out clears the session, including the cart.
- **Password reset:** `/password-reset/` emails a one-time link. With the console email
  backend (`EMAIL_BACKEND` in `config/settings.py`) the message prints in the `runserver`
  terminal; switch to an SMTP backend for real delivery.
- **Without JavaScript:** the tabs are links (`/login/?mode=register`) and the form posts a
  hidden `mode` field, so the right tab is shown after a failed submit. JavaScript only adds
  instant tab switching and the show/hide password button.

## 12. Payments (UPI, debit card, credit card)

After billing, UPI / debit / credit orders go to `/pay/<order>/`; Cash on Delivery skips it.

- **UPI:** two options. *Scan QR code* shows a QR for a standard `upi://pay` link (merchant ID, amount and
  order number), which any UPI app can scan or open; *Enter UPI ID* asks for a UPI ID (`name@bank`,
  validated) and sends a payment request to it.
- **Cards (debit or credit):** name on card, card number, expiry and CVV, all validated on the browser
  (live formatting and brand detection) and again on the server: any 16-digit number (15 for American
  Express; no checksum rule), a real MM/YY that is not
  expired, and a 3-digit CVV. Any 16-digit number is accepted;
  `4000 0000 0000 0002` is always declined so the failure path can be tried.
- **After payment:** the order becomes *Paid* with a reference number (`TXN...`), the cart is cleared and the
  customer lands on the order page. An unpaid order keeps its cart and shows *Complete payment*.
- **Privacy:** the full card number and CVV are validated and then discarded. Only the card brand and last four
  digits (and, for UPI, the UPI ID) are stored. The payment page is served with `no-store` caching.

**This is a demo.** There is no bank or gateway behind these forms: with `PAYMENT_DEMO_MODE` on (the default),
a valid form is accepted as a successful payment and the QR's "I have paid" button is taken on trust, because
nothing can confirm a real UPI payment without a gateway or bank callback. With it off
(`set PAYMENT_DEMO_MODE=0`), online methods are refused and customers are asked to use Cash on Delivery.
To take real payments, replace the acceptance step in `shop/views.py::pay` / `shop/payments.py` with a
PCI-compliant gateway (for cards, use the gateway's hosted fields rather than posting card numbers to this
server) and a callback or webhook that confirms the payment. `UPI_MERCHANT_VPA` (setting / environment
variable) is the UPI ID the QR points to; it defaults to a placeholder.

## 13. GST and bulk-offer savings

Listed prices **exclude GST**. The bill is worked out in `shop/cart.py::totals` using `shop/pricing.py`:

```
Subtotal            sum of unit price x quantity
- Bulk offer savings   (10 or more of an item cost Rs. 249 instead of Rs. 500, so Rs. 251 is saved)
= Taxable amount
+ CGST (9%) + SGST (9%)   GST_RATE = 18%, split equally; any odd paisa goes to SGST
= Total               this is the amount paid
```

The breakdown, the savings per item ("You save Rs.251") and the seller GSTIN appear on the cart, billing,
order and tracking pages, and the pay page charges the GST-inclusive total. Each order stores its own
subtotal, discount, taxable value, GST rate, CGST, SGST and total, so old orders keep the figures they were
billed with (orders placed before GST existed show no GST lines). Configure with environment variables
`GST_RATE` (default `18`) and `SELLER_GSTIN` (the default is a placeholder; set the real GSTIN before
issuing invoices). Admin edits to an order's items recalculate its totals with the order's stored rate.
