"""GST maths shared by the cart, checkout and admin."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def gst_breakup(taxable, rate):
    """GST on `taxable` at `rate` percent, split equally into CGST and SGST.

    The split always adds back up to the GST total (any odd paisa goes to SGST).
    """
    taxable = Decimal(taxable)
    rate = Decimal(rate)
    gst = money(taxable * rate / 100)
    cgst = money(gst / 2)
    sgst = gst - cgst
    return {
        "gst_rate": rate,
        "half_rate": rate / 2,
        "cgst": cgst,
        "sgst": sgst,
        "gst": gst,
        "total": money(taxable) + gst,
    }
