import reflex as rx
import asyncio
from landing_page_design_for_groundzero.models import BrandPresenceResult
from typing import List, Dict

DUMMY_RESULTS_TEMPLATE = [
    {
        "category": "Search Engines",
        "channel_name": "Google Search",
        "score": 85,
        "explanation_template": "Strong presence for {brand_name} with multiple first-page results and key products.",
        "rank": 1,
    },
    {
        "category": "E-commerce Platforms",
        "channel_name": "Amazon",
        "score": 70,
        "explanation_template": "Official store for {brand_name} present, good product listings, but some negative reviews impact score.",
        "rank": 2,
    },
    {
        "category": "Social Media",
        "channel_name": "Instagram",
        "score": 92,
        "explanation_template": "High engagement for {brand_name}, large follower base, consistent high-quality content.",
        "rank": 1,
    },
    {
        "category": "Social Media",
        "channel_name": "Twitter / X",
        "score": 65,
        "explanation_template": "Active account for {brand_name}, but lower engagement compared to Instagram. Room for improvement.",
        "rank": 3,
    },
    {
        "category": "Review Sites",
        "channel_name": "TrustPilot",
        "score": 55,
        "explanation_template": "Mixed reviews for {brand_name}, brand should actively manage its reputation here.",
        "rank": 4,
    },
]


def get_dummy_results(
    brand_name: str,
) -> List[BrandPresenceResult]:
    results = []
    for item_template in DUMMY_RESULTS_TEMPLATE:
        results.append(
            BrandPresenceResult(
                category=item_template["category"],
                channel_name=item_template["channel_name"],
                score=item_template["score"],
                explanation=item_template[
                    "explanation_template"
                ].format(brand_name=brand_name),
                rank=item_template["rank"],
            )
        )
    return results


class LandingState(rx.State):
    is_loading: bool = False
    error_message: str = ""
    search_results: List[BrandPresenceResult] = []
    submitted_brand_name: str = ""

    @rx.var
    def has_search_results(self) -> bool:
        return len(self.search_results) > 0

    async def _fetch_brand_data(
        self, brand_name: str
    ) -> List[BrandPresenceResult]:
        """
        Placeholder for actual data fetching logic.
        In a real app, this would make API calls to various services.
        """
        await asyncio.sleep(5)
        if brand_name.lower() == "error":
            raise ValueError(
                "Simulated API error for brand 'error'"
            )
        if brand_name.lower() == "nodata":
            return []
        return get_dummy_results(brand_name)

    @rx.event
    async def handle_search_submit(self, form_data: Dict):
        self.is_loading = True
        self.error_message = ""
        self.search_results = []
        yield
        brand_name_input = form_data.get(
            "brand_name_input", ""
        )
        if isinstance(brand_name_input, str):
            brand_name = brand_name_input.strip()
        else:
            brand_name = ""
        if not brand_name:
            self.error_message = (
                "Brand name cannot be empty."
            )
            self.is_loading = False
            return
        self.submitted_brand_name = brand_name
        try:
            results = await self._fetch_brand_data(
                brand_name
            )
            self.search_results = results
            if not results:
                self.error_message = f"No data found for '{brand_name}'. It might be a new brand or not in our current dataset."
        except Exception as e:
            self.error_message = (
                f"An error occurred: {str(e)}"
            )
            self.search_results = []
        finally:
            self.is_loading = False