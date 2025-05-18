import reflex as rx
from landing_page_design_for_groundzero.states.landing_state import LandingState
from landing_page_design_for_groundzero.components.navbar import navbar
from landing_page_design_for_groundzero.components.search_input_section import (
    search_input_section,
)
from landing_page_design_for_groundzero.components.results_display_section import (
    results_display_section,
)


def index() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(
                search_input_section(),
                results_display_section(),
                class_name="container mx-auto px-4 py-8 md:py-12 flex flex-col items-center gap-12",
            ),
            class_name="flex-grow",
        ),
        rx.el.footer(
            rx.el.p(
                "© 2024 GroundZero. All rights reserved.",
                class_name="text-sm text-slate-500 text-center",
            ),
            class_name="w-full p-6 bg-slate-100 border-t border-slate-200",
        ),
        class_name="min-h-screen flex flex-col bg-gradient-to-br from-slate-100 via-white to-indigo-50 text-slate-900",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=["/custom_styles.css"],
)
app.add_page(index)