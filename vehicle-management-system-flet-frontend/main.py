import flet as ft
import requests

API_BASE_URL = "http://127.0.0.1:8000/api"

PRIMARY = "#3B82F6"
SECONDARY = "#10B981"
DANGER = "#EF4444"
WARNING = "#F59E0B"
BG = "#0F172A"
CARD = "#1E293B"
TEXT_SUB = "#94A3B8"

def safe_number_format(value):
    """Convert a value to a string with thousand separators if it's a number, else return the string as is."""
    try:
        num = int(value)
        s = str(num)
        result = []
        for i, ch in enumerate(reversed(s)):
            if i > 0 and i % 3 == 0:
                result.append(',')
            result.append(ch)
        return ''.join(reversed(result))
    except (ValueError, TypeError):
        return str(value)

def main(page: ft.Page):
    page.title = "Vehicle Management System"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 12
    page.scroll = ft.ScrollMode.AUTO

    state = {"vehicle": None, "repairs": [], "oils": [], "appointments": []}
    current_reg = None

    search_input = ft.TextField(
        hint_text="Registration (e.g. ABC1234)",
        width=280,
        border_radius=12,
        border_color=PRIMARY,
        bgcolor="#1E293B",
        color="white",
        content_padding=16,
    )
    loader = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2, color=SECONDARY)
    main_content = ft.Container(expand=True)

    def toast(msg, error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, weight="bold"),
            bgcolor=DANGER if error else SECONDARY,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def stat_card(title, value_text, emoji, color):
        return ft.Container(
            bgcolor=CARD,
            border_radius=20,
            padding=20,
            expand=True,
            content=ft.Row([
                ft.Container(
                    content=ft.Text(emoji, size=28),
                    bgcolor="#1E293B",
                    padding=15,
                    border_radius=15,
                ),
                ft.Column([
                    ft.Text(title.upper(), size=11, weight="bold", color=TEXT_SUB),
                    ft.Text(value_text, size=20, weight="bold", color="white"),
                ], spacing=2),
            ]),
        )

    def build_scrollable_table(header_labels, rows, empty_msg, height=250):
        """Return a scrollable Column that contains the table (no selection highlight)."""
        if not rows:
            return ft.Container(
                content=ft.Text(empty_msg, size=12, color=TEXT_SUB),
                padding=20,
                height=height,
            )

        table_content = ft.Column(spacing=0)

        # Header
        table_content.controls.append(
            ft.Container(
                content=ft.Row(
                    [ft.Text(h, size=10, weight="bold", color=TEXT_SUB, expand=True) for h in header_labels],
                    spacing=8,
                ),
                padding=10,
                bgcolor="#1E293B",
                border_radius=8,
            )
        )

        # Data rows – uniform solid backgrounds
        for i, row in enumerate(rows):
            row_bg = CARD if i % 2 == 0 else "#2A3548"
            table_content.controls.append(
                ft.Container(
                    content=ft.Row(
                        [ft.Text(str(cell), size=12, color="white" if idx == 0 else TEXT_SUB, expand=True)
                         for idx, cell in enumerate(row)],
                        spacing=8,
                    ),
                    padding=12,
                    bgcolor=row_bg,
                    border_radius=8,
                )
            )

        return ft.Column(
            [table_content],
            scroll=ft.ScrollMode.AUTO,
            height=height,
        )

    def section_card(title, scrollable_table, emoji, height=280):
        return ft.Container(
            bgcolor=CARD,
            border_radius=20,
            padding=16,
            margin=8,
            content=ft.Column([
                ft.Row([ft.Text(emoji, size=20), ft.Text(title, size=18, weight="bold")], spacing=10),
                ft.Divider(height=1, color="white12"),
                scrollable_table,
            ]),
            expand=True,
        )

    def render_dashboard():
        v = state["vehicle"]
        if not v:
            main_content.content = ft.Column([
                ft.Container(expand=True),
                ft.Column([
                    ft.Text("🚗", size=60),
                    ft.Text("No vehicle loaded", size=20, weight="bold"),
                    ft.Text("Search for a registration", size=14, color=TEXT_SUB),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                ft.Container(expand=True),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            page.update()
            return

        reg = v.get("vehicle_regis_number", current_reg)
        km = v.get("current_milleage", 0)
        owner = v.get("customer_name", "N/A")
        phone = v.get("customer_phone_number", "N/A")

        alert_col = ft.Column(spacing=8)
        overview_txt = ft.Text("", size=13, color=TEXT_SUB)
        if state["oils"]:
            latest = state["oils"][0]
            last_m = latest.get("new_milleage", 0)
            last_date = latest.get("date_changed", "")
            if "T" in last_date:
                last_date = last_date.split("T")[0]
            overview_txt.value = f"Next Service: {safe_number_format(last_m)} km  •  {last_date}"
            due = last_m + 5000
            remaining = due - km
            if remaining <= 0:
                alert_col.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("⚠️", size=24),
                            ft.Text(f"Overdue! Due at {safe_number_format(due)} km", size=13, color=WARNING)
                        ], spacing=10),
                        bgcolor="#332101", border_radius=16, padding=14,
                    )
                )
            elif remaining <= 1000:
                alert_col.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("ℹ️", size=24),
                            ft.Text(f"Service due in {safe_number_format(remaining)} km", size=13, color=WARNING)
                        ], spacing=10),
                        bgcolor="#332101", border_radius=16, padding=14,
                    )
                )
        else:
            overview_txt.value = "No service records"

        # Prepare data rows
        oil_rows = []
        for o in state["oils"]:
            date_val = o.get("date_changed", "").split("T")[0]
            oil_rows.append([safe_number_format(o.get("new_milleage", 0)), date_val])

        repair_rows = []
        for r in state["repairs"]:
            date_val = r.get("date_repaired", "").split("T")[0]
            cost_val = r.get("costs", 0)
            cost_str = safe_number_format(cost_val)
            if not cost_str.startswith("Rs"):
                cost_str = "Rs " + cost_str
            repair_rows.append([r.get("description", "-"), cost_str, date_val])

        # --- FIX: Use 'time' (not 'time_slot') from API response ---
        app_rows = []
        for a in state["appointments"]:
            app_date = a.get("date", "-")
            if "T" in app_date:
                app_date = app_date.split("T")[0]
            app_time = a.get("time", "-")  # API returns 'time' field
            app_rows.append([app_date, app_time])

        # Build scrollable tables
        oils_table = build_scrollable_table(["Mileage (km)", "Date Changed"], oil_rows, "No oil changes", height=220)
        repairs_table = build_scrollable_table(["Description", "Cost", "Date"], repair_rows, "No repairs", height=280)
        apps_table = build_scrollable_table(["Date", "Time"], app_rows, "No visits", height=180)  # column header "Time"

        # Quick action fields
        b_date = ft.TextField(label="Date (YYYY-MM-DD)", width=160, dense=True, content_padding=12)
        b_time = ft.TextField(label="Time (HH:MM:SS)", width=140, dense=True, content_padding=12)  # changed label
        m_input = ft.TextField(label="New mileage (km)", width=180, dense=True, content_padding=12)

        def handle_booking(e):
            if not current_reg or not b_date.value or not b_time.value:
                toast("Fill both date and time", True)
                return
            try:
                # --- FIX: Use 'time' (not 'time_slot') in request body ---
                res = requests.post(API_BASE_URL + "/appointments/", json={
                    "vehicle": current_reg,
                    "date": b_date.value,
                    "time": b_time.value,   # changed from 'time_slot' to 'time'
                }).json()
                state["appointments"].insert(0, res)
                render_dashboard()
                b_date.value = ""
                b_time.value = ""
                toast("Appointment booked!")
            except Exception as ex:
                toast(str(ex), True)

        def handle_mileage(e):
            if not current_reg or not m_input.value:
                toast("Enter a mileage value", True)
                return
            try:
                val = int(m_input.value)
                requests.patch(API_BASE_URL + "/vehicles/" + current_reg + "/", json={"current_milleage": val}).raise_for_status()
                state["vehicle"]["current_milleage"] = val
                render_dashboard()
                m_input.value = ""
                toast("Odometer updated")
            except Exception as ex:
                toast(str(ex), True)

        quick_actions = ft.Container(
            bgcolor=CARD, border_radius=20, padding=20, margin=10,
            content=ft.Column([
                ft.Text("⚡ Quick Actions", size=18, weight="bold"),
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Text("Book Appointment", size=12, color=TEXT_SUB, weight="bold"),
                        ft.Row([b_date, b_time], wrap=True, spacing=8),
                        ft.ElevatedButton("📅 Book", on_click=handle_booking, style=ft.ButtonStyle(bgcolor=SECONDARY, color="white", padding=12)),
                    ], col={"xs": 12, "md": 6}),
                    ft.Column([
                        ft.Text("Update Odometer", size=12, color=TEXT_SUB, weight="bold"),
                        ft.Row([m_input, ft.ElevatedButton("📈 Update", on_click=handle_mileage, style=ft.ButtonStyle(bgcolor=PRIMARY, color="white", padding=12))], wrap=True, spacing=8),
                    ], col={"xs": 12, "md": 6}),
                ], spacing=20),
            ]),
        )

        header_row = ft.Row([
            ft.Column([
                ft.Text(reg, size=24, weight="bold"),
                overview_txt,
            ], expand=True),
            ft.ElevatedButton("🔄 Sync", on_click=lambda e: search_vehicle(), style=ft.ButtonStyle(bgcolor=PRIMARY, color="white", padding=12)),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        stats_row = ft.ResponsiveRow([
            ft.Column(stat_card("Odometer", safe_number_format(km) + " km", "📊", SECONDARY), col={"xs": 12, "sm": 4}),
            ft.Column(stat_card("Owner", owner, "👤", PRIMARY), col={"xs": 12, "sm": 4}),
            ft.Column(stat_card("Phone", phone, "📞", WARNING), col={"xs": 12, "sm": 4}),
        ], spacing=15)

        history_row = ft.ResponsiveRow([
            ft.Column(section_card("Oil History", oils_table, "🛢️", height=280), col={"xs": 12, "md": 4}),
            ft.Column(section_card("Repairs", repairs_table, "🔧", height=340), col={"xs": 12, "md": 4}),
            ft.Column(section_card("Visits", apps_table, "📆", height=240), col={"xs": 12, "md": 4}),
        ], spacing=10)

        main_content.content = ft.Column(
            [header_row, ft.Divider(height=20, color="transparent"), alert_col, stats_row, quick_actions, history_row],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )
        page.update()

    def search_vehicle(e=None):
        nonlocal current_reg
        reg = search_input.value.strip()
        if not reg:
            toast("Enter a registration", True)
            return
        current_reg = reg
        loader.visible = True
        search_input.disabled = True
        main_content.content = ft.Column([
            ft.Container(expand=True),
            ft.Column([
                ft.ProgressRing(color=PRIMARY),
                ft.Text("Searching...", size=14, color=TEXT_SUB),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            ft.Container(expand=True),
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        page.update()

        try:
            resp = requests.get(API_BASE_URL + "/vehicles/" + reg + "/", timeout=6)
            if resp.status_code == 404:
                raise Exception("Vehicle not found")
            resp.raise_for_status()
            vehicle = resp.json()
            repairs = requests.get(API_BASE_URL + "/vehicles/" + reg + "/repairs/", timeout=6).json() or []
            oils = requests.get(API_BASE_URL + "/vehicles/" + reg + "/oil_changes/", timeout=6).json() or []
            apps = requests.get(API_BASE_URL + "/vehicles/" + reg + "/appointments/", timeout=6).json() or []
            state.update({"vehicle": vehicle, "repairs": repairs, "oils": oils, "appointments": apps})
            render_dashboard()
        except Exception as ex:
            toast(str(ex), True)
            main_content.content = ft.Column([
                ft.Container(expand=True),
                ft.Column([
                    ft.Text("❌", size=48),
                    ft.Text("Error", size=20, weight="bold", color=DANGER),
                    ft.Text(str(ex), size=14, color=TEXT_SUB),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                ft.Container(expand=True),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            page.update()
        finally:
            loader.visible = False
            search_input.disabled = False
            page.update()

    header = ft.Container(
        bgcolor=CARD,
        padding=12,
        border=ft.Border(bottom=ft.BorderSide(1, "white12")),
        content=ft.Row([
            ft.Row([
                ft.Text("🚗", size=24),
                ft.Text("Vehicle Management system", size=20, weight="bold"),
            ], spacing=8),
            ft.Row([
                search_input,
                ft.ElevatedButton(content=ft.Text("🔍", size=18), on_click=search_vehicle, style=ft.ButtonStyle(bgcolor=PRIMARY, padding=12)),
                loader,
            ], spacing=8, wrap=True),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
    )

    # Welcome screen
    main_content.content = ft.Column([
        ft.Container(expand=True),
        ft.Column([
            ft.Text("🛡️", size=56),
            ft.Text("Vehicle Management System", size=28, weight="bold"),
            ft.Text("Enter vehicle registration to start.", size=14, color=TEXT_SUB),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
        ft.Container(expand=True),
    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(header, main_content)

if __name__ == "__main__":
    ft.app(target=main)