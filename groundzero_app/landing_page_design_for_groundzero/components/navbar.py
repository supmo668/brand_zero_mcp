import reflex as rx


def navbar() -> rx.Component:
    return rx.el.div(
        rx.el.a(
            rx.el.h1(
                "GroundZero",
                class_name="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600",
            ),
            href="/",
        ),
        class_name="w-full p-4 md:p-6 flex justify-start items-center bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-slate-200",
    )