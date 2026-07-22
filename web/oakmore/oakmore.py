"""Oakmore Billing — MVP UI (Reflex). Clients -> members -> itemized invoice preview."""
from __future__ import annotations
import os
import httpx
import reflex as rx

API = os.environ.get("GATEWAY_URL", "https://oakmore-billing-api.onrender.com").rstrip("/")
COMPANY_ID = os.environ.get("COMPANY_ID", "3")  # attentive tenant (MVP)

NAVY = "#10243A"
AMBER = "#FFB700"
BLUE = "#3470E0"
HEADERS = {"X-Company-Id": COMPANY_ID}


class State(rx.State):
    clients: list[dict] = []
    members: list[dict] = []
    lines: list[dict] = []
    client_id: int = 0
    client_name: str = ""
    total: str = ""
    loading: bool = False
    search: str = ""

    @rx.event
    def set_search(self, value: str):
        self.search = value

    @rx.event
    def back_to_clients(self):
        self.client_id = 0
        self.members, self.lines, self.total = [], [], ""

    @rx.event
    async def load_clients(self):
        self.loading = True
        yield
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.get(f"{API}/clients", params={"q": self.search, "limit": 50}, headers=HEADERS)
            self.clients = r.json() if r.status_code == 200 else []
        self.loading = False

    @rx.event
    async def open_client(self, cid: int, name: str):
        self.client_id, self.client_name = cid, name
        self.members, self.lines, self.total = [], [], ""
        self.loading = True
        yield
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.get(f"{API}/clients/{cid}/members", headers=HEADERS)
            self.members = r.json() if r.status_code == 200 else []
        self.loading = False

    @rx.event
    async def preview_invoice(self):
        self.loading = True
        yield
        async with httpx.AsyncClient(timeout=90) as c:
            r = await c.post(f"{API}/invoices/preview-lines", headers=HEADERS,
                             json={"client_id": self.client_id, "service_month": "2026-07-01"})
        if r.status_code == 200:
            d = r.json()
            self.total = d["total_fee"]
            self.lines = [{**l, "member_id": str(l["member_id"])}
                          for m in d["members"] for l in m["lines"]]
        self.loading = False


def header() -> rx.Component:
    return rx.hstack(
        rx.heading("Oakmore", color="white", size="6"),
        rx.text("Billing", color=AMBER, weight="bold"),
        rx.spacer(),
        rx.text("MVP", color="white", opacity="0.6"),
        width="100%", padding="1rem 1.5rem", bg=NAVY, align="center",
    )


def clients_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.input(placeholder="Search clients…", value=State.search,
                     on_change=State.set_search, width="20rem"),
            rx.button("Search", on_click=State.load_clients, bg=BLUE, color="white"),
        ),
        rx.foreach(State.clients, lambda c: rx.hstack(
            rx.text(c["client_name"], weight="medium"),
            rx.spacer(),
            rx.badge(c["client_status"]),
            rx.button("Open", size="1", bg=NAVY, color="white",
                      on_click=lambda: State.open_client(c["id"], c["client_name"])),
            width="100%", padding="0.5rem 0.75rem", border_bottom="1px solid #eee", align="center",
        )),
        width="100%", spacing="2",
    )


def client_detail() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading(State.client_name, size="5", color=NAVY),
            rx.spacer(),
            rx.button("Preview July invoice", on_click=State.preview_invoice, bg=AMBER, color=NAVY, weight="bold"),
        ),
        rx.text(f"{State.members.length()} active members"),
        rx.cond(State.total != "",
            rx.box(
                rx.heading(f"Invoice total: ${State.total}", size="4", color=BLUE),
                rx.foreach(State.lines, lambda l: rx.hstack(
                    rx.text(f"member {l['member_id']}", width="7rem", opacity="0.7"),
                    rx.text(l["product_code"], width="12rem"),
                    rx.spacer(),
                    rx.text(f"${l['amount']}", weight="medium"),
                    width="100%", padding="0.25rem 0", border_bottom="1px solid #f0f0f0",
                )),
                padding="1rem", border=f"1px solid {AMBER}", border_radius="8px", width="100%",
            ),
        ),
        width="100%", spacing="3",
    )


def index() -> rx.Component:
    return rx.vstack(
        header(),
        rx.box(
            rx.cond(State.loading, rx.spinner()),
            rx.cond(State.client_id == 0, clients_view(), client_detail()),
            padding="1.5rem", width="100%", max_width="900px",
        ),
        rx.button("← Clients", on_click=State.back_to_clients,
                  variant="ghost", margin="1rem", display=rx.cond(State.client_id == 0, "none", "block")),
        width="100%", align="center", spacing="0",
    )


app = rx.App()
app.add_page(index, on_load=State.load_clients, title="Oakmore Billing")
