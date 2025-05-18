import reflex as rx
from landing_page_design_for_groundzero.states.landing_state import LandingState
from landing_page_design_for_groundzero.components.results_table import results_table


def results_display_section() -> rx.Component:
    return rx.el.div(
        rx.cond(
            LandingState.is_loading,
            rx.el.div(
                rx.spinner(
                    class_name="text-purple-600 h-16 w-16"
                ),
                rx.el.p(
                    "Analyzing brand presence...",
                    class_name="text-xl text-slate-600 mt-4",
                ),
                class_name="flex flex-col items-center justify-center py-20 min-h-[300px]",
            ),
            rx.cond(
                LandingState.has_search_results,
                results_table(),
                rx.el.div(
                    rx.cond(
                        LandingState.submitted_brand_name
                        != "",
                        rx.el.p(
                            rx.cond(
                                LandingState.error_message
                                != "",
                                LandingState.error_message,
                                f"No results to display for '{LandingState.submitted_brand_name}'. This might be a new brand or an issue with data retrieval.",
                            ),
                            class_name="text-xl text-slate-600 text-center py-20",
                        ),
                        rx.el.p(
                            "Enter a brand name above and click 'Analyze Presence' to see the report.",
                            class_name="text-xl text-slate-600 text-center py-20",
                        ),
                    ),
                    class_name="w-full max-w-5xl mx-auto mt-10 p-6 md:p-8 bg-white rounded-xl shadow-lg",
                ),
            ),
        ),
        class_name="w-full",
    )