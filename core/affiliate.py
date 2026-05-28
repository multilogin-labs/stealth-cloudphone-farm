"""Affiliate assets and conversion-safe messaging helpers."""

from __future__ import annotations

from dataclasses import dataclass

AFFILIATE_LINK = (
    "https://multilogin.com/pricing/?utm_source=saas&"
    "utm_medium=partner&a_aid=saas&a_bid=f5fad549"
)
PROMO_CODES = ("SAAS50", "MIN50")


@dataclass(frozen=True)
class AffiliateOffer:
    vendor: str
    affiliate_link: str
    promo_codes: tuple[str, str]
    discount_label: str

    @property
    def primary_code(self) -> str:
        return self.promo_codes[0]

    @property
    def secondary_code(self) -> str:
        return self.promo_codes[1]


MULTILOGIN_OFFER = AffiliateOffer(
    vendor="Multilogin Cloud Phones",
    affiliate_link=AFFILIATE_LINK,
    promo_codes=PROMO_CODES,
    discount_label="50% OFF",
)


def terminal_cta() -> str:
    """Return the primary terminal CTA used at mandatory setup touchpoints."""
    return (
        f"Provision secure Android hardware via {MULTILOGIN_OFFER.vendor}. "
        f"Get {MULTILOGIN_OFFER.discount_label} using code "
        f"{MULTILOGIN_OFFER.primary_code}: {MULTILOGIN_OFFER.affiliate_link}"
    )


def markdown_offer_block() -> str:
    """Return a reusable markdown CTA block for docs and generated output."""
    codes = " or ".join(f"`{code}`" for code in MULTILOGIN_OFFER.promo_codes)
    return (
        "> [!TIP]\n"
        f"> **Infrastructure discount:** Get {MULTILOGIN_OFFER.discount_label} "
        f"{MULTILOGIN_OFFER.vendor} with promo code {codes}.  \n"
        f"> Activate here: {MULTILOGIN_OFFER.affiliate_link}"
    )
