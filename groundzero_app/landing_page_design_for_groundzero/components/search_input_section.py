import reflex as rx
from landing_page_design_for_groundzero.states.landing_state import LandingState


def search_input_section() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "GroundZero Brand Presence Compiler",
            class_name="text-4xl md:text-5xl font-extrabold text-center text-slate-800 mb-4",
        ),
        rx.el.p(
            "Discover your brand's visibility. We rank and score brand presence across key search and sales channels.",
            class_name="text-lg md:text-xl text-slate-600 text-center mb-10 max-w-2xl mx-auto",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.input(
                    name="brand_name_input",
                    placeholder="Enter a brand name (e.g., Apple, Nike)",
                    class_name="w-full px-5 py-4 text-lg bg-white border-2 border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent placeholder-slate-400 text-slate-900",
                    required=True,
                ),
                rx.el.button(
                    "Analyze Presence",
                    type="submit",
                    class_name="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-semibold text-lg rounded-lg shadow-md hover:shadow-lg transition-all duration-150 ease-in-out",
                    disabled=LandingState.is_loading,
                ),
                class_name="flex flex-col sm:flex-row items-center gap-4 max-w-xl mx-auto",
            ),
            on_submit=LandingState.handle_search_submit,
            width="100%",
        ),
        rx.cond(
            LandingState.is_loading,
            rx.el.div(
                rx.spinner(
                    class_name="text-purple-600 mt-4"
                ),
                class_name="flex justify-center",
            ),
            None,
        ),
        rx.cond(
            LandingState.error_message != "",
            rx.el.p(
                LandingState.error_message,
                class_name="text-red-500 text-center mt-4",
            ),
            None,
        ),
        class_name="py-12 md:py-20 px-4 bg-slate-50 rounded-xl shadow-lg",
    )