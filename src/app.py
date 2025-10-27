from __future__ import annotations

import asyncio
from datetime import datetime

import flet as ft


def main(page: ft.Page) -> None:
    """Configure page and build the chat experience."""

    page.title = "Conversational Copilot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL_400, use_material3=True)
    page.padding = 0
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_min_width = 420
    page.window_min_height = 640

    page.appbar = ft.AppBar(
        bgcolor=ft.Colors.WHITE,
        surface_tint_color=ft.Colors.WHITE,
        elevation=4,
        leading_width=60,
        leading=ft.Container(
            margin=ft.margin.all(8),
            padding=ft.padding.all(8),
            width=40,
            height=40,
            border_radius=ft.border_radius.all(14),
            bgcolor=ft.Colors.TEAL_100,
            content=ft.Icon(
                ft.Icons.STAR_ROUNDED,
                size=20,
                color=ft.Colors.TEAL_700,
            ),
        ),
        title=ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "Conversational Copilot",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.BLUE_GREY_900,
                ),
                ft.Text(
                    "Prototype chat interface powered by Flet",
                    size=12,
                    color=ft.Colors.BLUE_GREY_400,
                ),
            ],
        ),
        center_title=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.SHIELD_OUTLINED,
                icon_color=ft.Colors.BLUE_GREY_300,
                tooltip="Secure session",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            ),
            ft.Container(width=12),
        ],
    )

    message_list = ft.ListView(
        expand=True,
        spacing=16,
        padding=ft.padding.symmetric(horizontal=8, vertical=16),
        auto_scroll=True,
    )

    typing_indicator = ft.Row(
        visible=False,
        alignment=ft.MainAxisAlignment.START,
        controls=[
            ft.Container(
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                bgcolor=ft.Colors.BLUE_GREY_50,
                border_radius=ft.border_radius.only(
                    top_left=18,
                    top_right=18,
                    bottom_left=6,
                    bottom_right=18,
                ),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.ProgressRing(
                            width=18,
                            height=18,
                            stroke_width=2,
                            color=ft.Colors.TEAL_400,
                        ),
                        ft.Text(
                            "The model is thinking...",
                            size=12,
                            color=ft.Colors.BLUE_GREY_400,
                        ),
                    ],
                ),
            )
        ],
    )

    def build_tool_invocation_card(
        invocation: dict[str, object],
        *,
        is_user: bool,
    ) -> ft.Control:
        """Render details about a tool call inside a message bubble."""

        name = str(invocation.get("name", "Tool invocation"))
        status = str(invocation.get("status", "running")).lower()
        summary = invocation.get("summary")
        result = invocation.get("result")
        arguments = invocation.get("arguments")

        status_palette = {
            "completed": (ft.Colors.GREEN_50, ft.Colors.GREEN_600),
            "running": (ft.Colors.AMBER_50, ft.Colors.AMBER_600),
            "failed": (ft.Colors.RED_50, ft.Colors.RED_600),
        }
        status_bg, status_fg = status_palette.get(
            status,
            (ft.Colors.BLUE_GREY_50, ft.Colors.BLUE_GREY_600),
        )

        status_chip = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=ft.border_radius.all(999),
            bgcolor=status_bg,
            content=ft.Text(
                value=status.capitalize(),
                size=11,
                weight=ft.FontWeight.W_600,
                color=status_fg,
            ),
        )

        header = ft.Row(
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=30,
                    height=30,
                    border_radius=ft.border_radius.all(12),
                    bgcolor=(ft.Colors.WHITE if is_user else ft.Colors.TEAL_50),
                    content=ft.Icon(
                        ft.Icons.TUNE_ROUNDED,
                        size=16,
                        color=ft.Colors.TEAL_600,
                    ),
                ),
                ft.Text(
                    value=name,
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.BLUE_GREY_800,
                ),
                status_chip,
            ],
        )

        detail_controls: list[ft.Control] = [header]

        if summary:
            detail_controls.append(
                ft.Text(
                    value=str(summary),
                    size=12,
                    color=ft.Colors.BLUE_GREY_600,
                    selectable=True,
                )
            )

        argument_sections: list[ft.Control] = []
        if arguments:
            argument_rows: list[ft.Control] = []
            if isinstance(arguments, dict):
                for key, value in arguments.items():
                    argument_rows.append(
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    value=f"{key}:",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLUE_GREY_400,
                                ),
                                ft.Text(
                                    value=str(value),
                                    size=12,
                                    color=ft.Colors.BLUE_GREY_700,
                                    selectable=True,
                                ),
                            ],
                        )
                    )
            else:
                argument_rows.append(
                    ft.Text(
                        value=str(arguments),
                        size=12,
                        color=ft.Colors.BLUE_GREY_700,
                        selectable=True,
                    )
                )

            argument_sections.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    margin=ft.margin.only(top=4),
                    border_radius=ft.border_radius.all(12),
                    bgcolor=(ft.Colors.TEAL_100 if is_user else ft.Colors.WHITE),
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_50),
                    content=ft.Column(
                        spacing=6,
                        controls=argument_rows,
                    ),
                )
            )

        detail_controls.extend(argument_sections)

        if result:
            detail_controls.append(
                ft.Text(
                    value=str(result),
                    size=12,
                    color=ft.Colors.BLUE_GREY_600,
                    selectable=True,
                )
            )

        return ft.Container(
            margin=ft.margin.only(top=8),
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            border_radius=ft.border_radius.all(18),
            bgcolor=(ft.Colors.WHITE if is_user else ft.Colors.BLUE_GREY_50),
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=detail_controls,
            ),
        )

    def build_message(
        role: str,
        text: str,
        tool_invocation: dict[str, object] | None = None,
    ) -> ft.Control:
        """Create a styled chat bubble for the given role."""

        is_user = role == "user"
        bubble_color = ft.Colors.TEAL_500 if is_user else ft.Colors.WHITE
        bubble_text_color = ft.Colors.WHITE if is_user else ft.Colors.BLUE_GREY_900
        timestamp = datetime.now().strftime("%H:%M")

        avatar_icon = (
            ft.Icons.PERSON_ROUNDED if is_user else ft.Icons.SMART_TOY_OUTLINED
        )
        avatar_color = ft.Colors.TEAL_ACCENT_700 if is_user else ft.Colors.BLUE_GREY_200

        avatar = ft.CircleAvatar(
            radius=18,
            bgcolor=avatar_color,
            content=ft.Icon(avatar_icon, size=20, color=ft.Colors.WHITE),
        )

        text_length = len(text)
        longest_token = max(
            (len(token) for token in text.replace("\n", " ").split()),
            default=1,
        )
        available_width = (page.width or page.window_width or 640) - 220
        bubble_max_width = max(220, min(520, available_width))
        estimated_width = min(
            bubble_max_width,
            max(220, longest_token * 9, text_length * 5),
        )

        message_controls: list[ft.Control] = [
            ft.Text(
                value=text,
                size=14,
                color=bubble_text_color,
                selectable=True,
                max_lines=None,
                overflow=ft.TextOverflow.CLIP,
            )
        ]

        if tool_invocation:
            message_controls.append(
                build_tool_invocation_card(
                    tool_invocation,
                    is_user=is_user,
                )
            )

        timestamp_row = ft.Row(
            spacing=6,
            alignment=(
                ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            ),
            controls=[
                ft.Icon(
                    ft.Icons.SCHEDULE_ROUNDED,
                    size=12,
                    color=ft.Colors.BLUE_GREY_200,
                ),
                ft.Text(
                    value=timestamp,
                    size=11,
                    color=ft.Colors.BLUE_GREY_200,
                ),
            ],
        )

        message_controls.append(timestamp_row)

        bubble = ft.Container(
            width=estimated_width,
            bgcolor=bubble_color,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=ft.border_radius.only(
                top_left=18,
                top_right=18,
                bottom_left=18 if is_user else 6,
                bottom_right=6 if is_user else 18,
            ),
            content=ft.Column(
                spacing=8,
                tight=True,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.END
                    if is_user
                    else ft.CrossAxisAlignment.START
                ),
                controls=message_controls,
            ),
        )

        bubble_row = ft.Row(
            alignment=(
                ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            ),
            spacing=12,
            controls=[bubble, avatar] if is_user else [avatar, bubble],
        )

        return bubble_row

    def add_message(
        role: str,
        text: str,
        *,
        tool_invocation: dict[str, object] | None = None,
    ) -> None:
        message_list.controls.append(
            build_message(
                role,
                text,
                tool_invocation=tool_invocation,
            )
        )

    message_input = ft.TextField(
        hint_text="Send a message…",
        multiline=True,
        min_lines=1,
        max_lines=4,
        expand=True,
        border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        cursor_color=ft.Colors.TEAL_500,
        selection_color=ft.Colors.TEAL_100,
    )

    send_button = ft.FilledButton(
        text="Send",
        icon=ft.Icons.SEND_ROUNDED,
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TEAL_500,
                ft.ControlState.HOVERED: ft.Colors.TEAL_600,
                ft.ControlState.PRESSED: ft.Colors.TEAL_700,
            },
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=16),
        ),
    )

    async def fake_llm_response(prompt: str) -> None:
        typing_indicator.visible = True
        send_button.disabled = True
        page.update()

        await asyncio.sleep(0.9)

        synthesized_reply = (
            "Thanks for sharing! Here's a quick reflection: "
            f"{prompt.strip().capitalize()} sounds interesting - "
            "let's explore that together."
        )

        typing_indicator.visible = False

        normalized_prompt = prompt.strip()
        preview = (
            f"{normalized_prompt[:60]}…"
            if len(normalized_prompt) > 60
            else normalized_prompt
        ) or "general follow-up"

        tool_invocation = {
            "name": "context.search_knowledge",
            "status": "completed",
            "summary": "Retrieved supporting snippets to ground the answer.",
            "arguments": {
                "query": preview,
                "top_k": 3,
            },
            "result": "3 relevant notes were surfaced for continued exploration.",
        }

        add_message(
            "assistant",
            synthesized_reply,
            tool_invocation=tool_invocation,
        )
        send_button.disabled = False
        page.update()

    def handle_submit(_: ft.ControlEvent) -> None:
        user_text = (message_input.value or "").strip()
        if not user_text:
            return

        add_message("user", user_text)
        message_input.value = ""
        page.update()

        async def _runner() -> None:
            await fake_llm_response(user_text)

        page.run_task(_runner)

    message_input.on_submit = handle_submit
    send_button.on_click = handle_submit

    input_area = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.border_radius.all(24),
        padding=ft.padding.symmetric(horizontal=18, vertical=14),
        border=ft.border.all(1, ft.Colors.BLUE_GREY_50),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    ft.Icons.MESSAGE_OUTLINED,
                    size=22,
                    color=ft.Colors.BLUE_GREY_300,
                ),
                message_input,
                send_button,
            ],
        ),
    )

    chat_card = ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.border_radius.all(32),
        padding=ft.padding.symmetric(horizontal=28, vertical=24),
        shadow=ft.BoxShadow(
            blur_radius=32,
            spread_radius=-8,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 18),
        ),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            expand=True,
            spacing=18,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        spacing=12,
                        controls=[
                            ft.Container(expand=True, content=message_list),
                            typing_indicator,
                        ],
                    ),
                ),
                input_area,
            ],
        ),
    )

    main_layout = ft.Container(
        expand=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        padding=ft.padding.symmetric(horizontal=16, vertical=24),
        content=ft.ResponsiveRow(
            columns=1,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    col={"xs": 1, "sm": 1, "md": 1, "lg": 1},
                    expand=True,
                    padding=ft.padding.all(2),
                    alignment=ft.alignment.top_center,
                    content=chat_card,
                )
            ],
        ),
    )

    page.add(main_layout)

    def on_page_mount(_: ft.ControlEvent) -> None:
        page.set_focus(message_input)

    page.on_mount = on_page_mount

    add_message(
        "assistant",
        "Hi there! I'm your virtual copilot. How can I help today?",
    )
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
