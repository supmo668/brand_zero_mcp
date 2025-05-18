import reflex as rx
from landing_page_design_for_groundzero.states.landing_state import LandingState
from landing_page_design_for_groundzero.models import BrandPresenceResult


def render_table_row(
    result: BrandPresenceResult,
) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            result.category,
            class_name="px-5 py-4 whitespace-nowrap text-sm text-slate-700",
        ),
        rx.el.td(
            result.channel_name,
            class_name="px-5 py-4 whitespace-nowrap text-sm font-medium text-slate-900",
        ),
        rx.el.td(
            rx.el.span(
                result.score,
                class_name=rx.cond(
                    result.score >= 80,
                    "text-green-600 font-semibold",
                    rx.cond(
                        result.score >= 60,
                        "text-yellow-600 font-semibold",
                        "text-red-600 font-semibold",
                    ),
                ),
            ),
            class_name="px-5 py-4 whitespace-nowrap text-sm text-center",
        ),
        rx.el.td(
            result.explanation,
            class_name="px-5 py-4 text-sm text-slate-600 min-w-[300px]",
        ),
        class_name="border-b border-slate-200 hover:bg-slate-50 transition-colors duration-150",
    )


def results_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Brand Presence Report for: ",
            rx.el.span(
                LandingState.submitted_brand_name,
                class_name="text-purple-700",
            ),
            class_name="text-2xl md:text-3xl font-bold text-slate-800 mb-6 text-center",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Category",
                            class_name="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100 rounded-tl-lg",
                        ),
                        rx.el.th(
                            "Channel",
                            class_name="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100",
                        ),
                        rx.el.th(
                            "Score",
                            class_name="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100",
                        ),
                        rx.el.th(
                            "Explanation",
                            class_name="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100 rounded-tr-lg",
                        ),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        LandingState.search_results,
                        render_table_row,
                    )
                ),
                class_name="min-w-full divide-y divide-slate-200 bg-white shadow-xl rounded-lg",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="w-full max-w-5xl mx-auto mt-10 p-6 md:p-8 bg-white rounded-xl shadow-2xl",
    )