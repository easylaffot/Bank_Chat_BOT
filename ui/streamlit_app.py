"""Streamlit client for the shopping assistant, FAQ, and cart APIs."""

import os
from typing import Any

import requests
import streamlit as st


st.set_page_config(
    page_title="Laptop Shopping Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------------------------------------------------
# Professional dark theme
# -------------------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;

        --page-background: #0b1120;
        --sidebar-background: #111827;
        --surface: #172033;
        --surface-raised: #1e293b;
        --surface-hover: #263449;

        --primary-text: #f8fafc;
        --secondary-text: #cbd5e1;
        --muted-text: #94a3b8;

        --accent: #22c55e;
        --accent-hover: #16a34a;
        --accent-soft: rgba(34, 197, 94, 0.12);

        --border: #334155;
        --warning: #f59e0b;
        --error: #ef4444;
    }

    /* Main page */
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .stApp {
        background-color: var(--page-background) !important;
        color: var(--primary-text) !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(11, 17, 32, 0.96) !important;
    }

    [data-testid="stToolbar"] {
        color: var(--primary-text) !important;
    }

    /* Main content width and spacing */
    .block-container {
        max-width: 1280px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    /* Typography */
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: var(--primary-text) !important;
        font-family: Inter, "Segoe UI", Arial, sans-serif !important;
        letter-spacing: -0.02em;
    }

    h1 {
        font-size: clamp(2.25rem, 5vw, 4rem) !important;
        font-weight: 750 !important;
        line-height: 1.08 !important;
    }

    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    h3 {
        font-size: 1.45rem !important;
        font-weight: 650 !important;
    }

    p,
    li,
    label,
    span {
        color: var(--secondary-text);
    }

    [data-testid="stMarkdownContainer"] p {
        color: var(--secondary-text) !important;
        line-height: 1.65;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: var(--muted-text) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div {
        background-color: var(--sidebar-background) !important;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: var(--primary-text) !important;
    }

    /* Widget labels */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stWidgetLabel"] label {
        color: var(--primary-text) !important;
        font-weight: 600 !important;
    }

    /* Text inputs and text areas */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        background-color: var(--surface) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        caret-color: var(--accent) !important;
        box-shadow: none !important;
    }

    [data-testid="stTextArea"] textarea {
        min-height: 120px;
        padding: 1rem !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stNumberInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-soft) !important;
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder,
    [data-testid="stNumberInput"] input::placeholder {
        color: var(--muted-text) !important;
        opacity: 1 !important;
    }

    /* BaseWeb input wrappers */
    [data-baseweb="input"],
    [data-baseweb="base-input"],
    [data-baseweb="textarea"],
    [data-baseweb="select"] > div {
        background-color: var(--surface) !important;
        color: var(--primary-text) !important;
        border-color: var(--border) !important;
    }

    [data-baseweb="input"] *,
    [data-baseweb="base-input"] *,
    [data-baseweb="textarea"] *,
    [data-baseweb="select"] * {
        color: var(--primary-text) !important;
    }

    /* Select menus */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background-color: var(--surface-raised) !important;
        color: var(--primary-text) !important;
        border: 1px solid var(--border) !important;
    }

    [role="option"] {
        background-color: var(--surface-raised) !important;
        color: var(--primary-text) !important;
    }

    [role="option"]:hover {
        background-color: var(--surface-hover) !important;
    }

    [role="option"] * {
        color: var(--primary-text) !important;
    }

    /* Radio buttons */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label span,
    [data-testid="stRadio"] p {
        color: var(--primary-text) !important;
    }

    /* Forms */
    [data-testid="stForm"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Product and content containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(
            145deg,
            var(--surface),
            var(--surface-raised)
        ) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        color: var(--primary-text) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
        overflow: visible !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] span,
    [data-testid="stVerticalBlockBorderWrapper"] label {
        color: var(--secondary-text) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] h1,
    [data-testid="stVerticalBlockBorderWrapper"] h2,
    [data-testid="stVerticalBlockBorderWrapper"] h3,
    [data-testid="stVerticalBlockBorderWrapper"] h4 {
        color: var(--primary-text) !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: rgba(11, 17, 32, 0.78) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        min-width: 0 !important;
        overflow: visible !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] div {
        color: var(--muted-text) !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: var(--primary-text) !important;
        font-size: clamp(1.35rem, 2.2vw, 2rem) !important;
        line-height: 1.25 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }

    /* Buttons */
    div.stButton > button,
    div.stFormSubmitButton > button {
        min-height: 44px;
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface-raised) !important;
        color: var(--primary-text) !important;
        font-weight: 700 !important;
        transition:
            background-color 0.2s ease,
            border-color 0.2s ease,
            transform 0.2s ease;
    }

    div.stButton > button *,
    div.stFormSubmitButton > button * {
        color: inherit !important;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
        color: #07120b !important;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background-color: var(--surface-hover) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateY(-1px);
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background-color: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        color: #ffffff !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        background-color: var(--surface-raised) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--primary-text) !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] div {
        color: var(--primary-text) !important;
    }

    /* Dividers */
    [data-testid="stDivider"] {
        border-color: var(--border) !important;
    }

    hr {
        border-color: var(--border) !important;
    }

    /* Custom price component */
    .product-price-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.75rem;
        width: 100%;
        margin: 1rem 0 1.25rem;
        padding: 0.9rem 1rem;
        background-color: rgba(11, 17, 32, 0.72);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: visible !important;
    }

    .product-price-label {
        color: var(--muted-text) !important;
        font-size: 0.9rem;
        font-weight: 650;
    }

    .product-price-value {
        display: inline-block;
        max-width: 100%;
        color: var(--accent) !important;
        font-family: Inter, "Segoe UI", Arial, sans-serif;
        font-size: clamp(1.4rem, 3vw, 2rem);
        font-weight: 800;
        font-variant-numeric: tabular-nums;
        line-height: 1.2;
        overflow: visible !important;
        white-space: nowrap !important;
        text-overflow: clip !important;
    }

    .eyebrow {
        color: var(--accent) !important;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .app-subtitle {
        color: var(--muted-text) !important;
        font-size: 1.03rem;
        margin-top: -0.5rem;
        margin-bottom: 2rem;
    }

    .product-identity {
        color: var(--muted-text) !important;
        font-size: 0.9rem;
        margin-top: -0.5rem;
        margin-bottom: 0.5rem;
    }

    .section-description {
        color: var(--secondary-text) !important;
        font-size: 1.02rem;
        margin-bottom: 1.5rem;
    }

    /* Spinner */
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span {
        color: var(--primary-text) !important;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.5rem;
        }

        h1 {
            font-size: 2.2rem !important;
        }

        .product-price-row {
            align-items: flex-start;
            flex-direction: column;
        }

        .product-price-value {
            white-space: normal !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


DEFAULT_API_ROOT = os.getenv(
    "STREAMLIT_API_BASE_URL",
    os.getenv(
        "SHOPPING_API_URL",
        "http://127.0.0.1:8000/api/v1",
    ),
)


def format_currency(value: Any) -> str:
    """Format an amount as Indian rupees without truncation."""
    try:
        amount = int(float(value))
    except (TypeError, ValueError):
        amount = 0

    return f"₹{amount:,}"


def api_request(
    method: str,
    api_root: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    """Send a request to the FastAPI backend."""

    try:
        response = requests.request(
            method,
            f"{api_root.rstrip('/')}/{path.lstrip('/')}",
            json=payload,
            timeout=120,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not reach the FastAPI server. "
            "Check the API URL and confirm that FastAPI is running."
        ) from exc

    if not response.ok:
        try:
            body = response.json()
            detail = body.get("detail", body)
        except ValueError:
            detail = response.text

        raise RuntimeError(
            f"API returned status {response.status_code}: {detail}"
        )

    return response.json()


def render_product(
    product: dict[str, Any],
    api_root: str,
    *,
    show_cart_action: bool = False,
) -> None:
    """Render one product recommendation card."""

    product_id = product.get("id", "")
    brand = product.get("brand", "")
    model_name = product.get("model_name", "Laptop")
    category = product.get("category", "Laptop")
    price = format_currency(product.get("price", 0))

    with st.container(border=True):
        st.markdown(f"### {brand} {model_name}")
        st.markdown(
            f'<p class="product-identity">{product_id} · {category}</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="product-price-row">
                <span class="product-price-label">Price</span>
                <strong class="product-price-value">{price}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        specs = st.columns(4)

        specs[0].metric(
            "Memory",
            f"{product.get('ram_gb', '—')} GB",
        )

        specs[1].metric(
            "Storage",
            f"{product.get('storage_gb', '—')} GB",
        )

        specs[2].metric(
            "Rating",
            f"{product.get('rating', '—')} / 5",
        )

        inventory = product.get("inventory", {})

        if inventory:
            if inventory.get("in_stock"):
                delivery_value = f"{inventory.get('delivery_days', '—')} days"
            else:
                delivery_value = "Unavailable"

            specs[3].metric("Delivery", delivery_value)
        else:
            specs[3].metric(
                "Processor",
                product.get("processor", "—"),
            )

        processor = product.get("processor")

        if processor:
            st.markdown(f"**Processor:** {processor}")

        if product.get("comparison_score") is not None:
            st.caption(
                f"Comparison score: {product['comparison_score']:.1f} · "
                f"Rank: {product.get('comparison_rank', '—')}"
            )

        budget_check = product.get("budget_check")

        if budget_check:
            remaining_budget = format_currency(
                budget_check.get("remaining_budget", 0)
            )
            st.caption(f"Remaining budget: {remaining_budget}")

        if show_cart_action:
            if st.button(
                "Add to cart",
                key=f"add-{product_id}",
                type="primary",
            ):
                try:
                    api_request(
                        "POST",
                        api_root,
                        "/cart/add",
                        {
                            "product_id": product_id,
                            "quantity": 1,
                        },
                    )

                    st.session_state["cart_notice"] = (
                        f"Added {model_name} to your cart."
                    )

                    st.rerun()

                except RuntimeError as exc:
                    st.error(str(exc))


def render_shopping_view(api_root: str) -> None:
    """Render the AI shopping recommendation view."""

    st.markdown(
        '<p class="eyebrow">Product guidance</p>',
        unsafe_allow_html=True,
    )

    st.header("Find the right laptop")

    st.markdown(
        """
        <p class="section-description">
            Describe your requirements and receive a ranked recommendation
            checked against price, inventory, and delivery information.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("shopping-query-form"):
        query = st.text_area(
            "What are you looking for?",
            placeholder=(
                "For example: a laptop under 60000 with "
                "16GB RAM for Python programming"
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "Get recommendations",
            type="primary",
        )

    if submitted:
        if not query.strip():
            st.warning(
                "Enter a few details about the laptop you need."
            )
        else:
            with st.spinner(
                "Comparing products and checking availability..."
            ):
                try:
                    result = api_request(
                        "POST",
                        api_root,
                        "/shopping-assistant",
                        {"query": query.strip()},
                    )

                    st.session_state["shopping_result"] = result

                except RuntimeError as exc:
                    st.error(str(exc))

    result = st.session_state.get("shopping_result")

    if not result:
        return

    if result.get("error"):
        st.warning(
            result["error"].get(
                "message",
                "No recommendation is currently available.",
            )
        )

    recommendation = result.get("recommendation")

    if recommendation:
        st.subheader("Recommended for you")

        render_product(
            recommendation,
            api_root,
            show_cart_action=True,
        )

        st.markdown("#### Why this product")

        st.write(
            recommendation.get(
                "reason",
                result.get(
                    "reason",
                    "Selected from the matching products.",
                ),
            )
        )

    alternatives = result.get("alternatives", [])

    if alternatives:
        st.subheader("Other suitable options")

        for product in alternatives:
            render_product(
                product,
                api_root,
                show_cart_action=True,
            )


def render_faq_view(api_root: str) -> None:
    """Render the RAG-powered FAQ view."""

    st.markdown(
        '<p class="eyebrow">Help and policies</p>',
        unsafe_allow_html=True,
    )

    st.header("Ask about delivery, returns, warranty, or payment")

    st.markdown(
        """
        <p class="section-description">
            Answers are generated from the store's FAQ knowledge base
            and include the source documents used.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("faq-question-form"):
        question = st.text_input(
            "Your question",
            placeholder="What warranty is available?",
        )

        submitted = st.form_submit_button(
            "Find an answer",
            type="primary",
        )

    if submitted:
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner(
                "Searching the FAQ knowledge base..."
            ):
                try:
                    st.session_state["faq_result"] = api_request(
                        "POST",
                        api_root,
                        "/faq",
                        {"question": question.strip()},
                    )

                except RuntimeError as exc:
                    st.error(str(exc))

    result = st.session_state.get("faq_result")

    if result:
        with st.container(border=True):
            st.subheader("Answer")
            st.write(result.get("answer", ""))

            sources = result.get("sources", [])

            if sources:
                st.caption(
                    "Sources: " + " · ".join(sources)
                )


def render_cart_view(api_root: str) -> None:
    """Render the shopping cart view."""

    st.markdown(
        '<p class="eyebrow">Your selection</p>',
        unsafe_allow_html=True,
    )

    st.header("Shopping cart")

    if notice := st.session_state.pop(
        "cart_notice",
        None,
    ):
        st.success(notice)

    try:
        cart = api_request(
            "GET",
            api_root,
            "/cart",
        )
    except RuntimeError as exc:
        st.error(str(exc))
        return

    summary, total = st.columns(2)

    summary.metric(
        "Items",
        cart.get("total_items", 0),
    )

    total.metric(
        "Subtotal",
        format_currency(cart.get("total_price", 0)),
    )

    items = cart.get("items", [])

    if items:
        st.subheader("In your cart")

        for item in items:
            with st.container(border=True):
                label, quantity, amount = st.columns(
                    [4, 1, 2]
                )

                label.markdown(
                    f"**{item['brand']} {item['model_name']}**"
                )

                label.caption(item["product_id"])

                quantity.markdown(
                    f"**Qty:** {item['quantity']}"
                )

                amount.markdown(
                    f"**{format_currency(item['line_total'])}**"
                )
    else:
        st.info("Your cart is empty.")

    try:
        catalog = api_request(
            "GET",
            api_root,
            "/products?limit=100&offset=0",
        )

        available_products = [
            item
            for item in catalog.get("items", [])
            if item.get("stock_quantity", 0) > 0
        ]

    except RuntimeError as exc:
        st.error(str(exc))
        return

    st.divider()
    st.subheader("Add a product")

    products_by_id = {
        item["id"]: item
        for item in available_products
    }

    if products_by_id:
        with st.form("cart-add-form"):
            selected_id = st.selectbox(
                "Available laptop",
                options=list(products_by_id),
                format_func=lambda product_id: (
                    f"{products_by_id[product_id]['brand']} "
                    f"{products_by_id[product_id]['model_name']} · "
                    f"{format_currency(products_by_id[product_id]['price'])}"
                ),
            )

            maximum = (
                products_by_id[selected_id]["stock_quantity"]
                if selected_id
                else 1
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=max(1, maximum),
                value=1,
                step=1,
            )

            add_submitted = st.form_submit_button(
                "Add selected product",
                type="primary",
            )

        if add_submitted and selected_id:
            try:
                api_request(
                    "POST",
                    api_root,
                    "/cart/add",
                    {
                        "product_id": selected_id,
                        "quantity": int(quantity),
                    },
                )

                st.session_state["cart_notice"] = (
                    "Product added to your cart."
                )

                st.rerun()

            except RuntimeError as exc:
                st.error(str(exc))
    else:
        st.warning(
            "No products are currently available to add."
        )

    if items:
        with st.form("cart-remove-form"):
            item_ids = [
                item["product_id"]
                for item in items
            ]

            selected_remove_id = st.selectbox(
                "Remove product",
                options=item_ids,
                format_func=lambda product_id: next(
                    (
                        f"{item['brand']} "
                        f"{item['model_name']} · "
                        f"{product_id}"
                    )
                    for item in items
                    if item["product_id"] == product_id
                ),
            )

            remove_submitted = st.form_submit_button(
                "Remove product"
            )

        if remove_submitted:
            try:
                api_request(
                    "POST",
                    api_root,
                    "/cart/remove",
                    {"product_id": selected_remove_id},
                )

                st.session_state["cart_notice"] = (
                    "Product removed from your cart."
                )

                st.rerun()

            except RuntimeError as exc:
                st.error(str(exc))

        if st.button("Clear cart"):
            try:
                api_request(
                    "DELETE",
                    api_root,
                    "/cart/clear",
                )

                st.session_state["cart_notice"] = (
                    "Cart cleared."
                )

                st.rerun()

            except RuntimeError as exc:
                st.error(str(exc))


def main() -> None:
    """Run the Streamlit application."""

    with st.sidebar:
        st.markdown("### 💻 Laptop Assistant")

        st.caption(
            "SHOPPING · SUPPORT · CART"
        )

        api_root = st.text_input(
            "FastAPI base URL",
            value=DEFAULT_API_ROOT,
        ).strip()

        view = st.radio(
            "Workspace",
            ["Shop", "FAQ", "Cart"],
            horizontal=False,
        )

        st.divider()

        st.caption(
            "Recommendations use your catalog, "
            "budget preferences, and live inventory records."
        )

    st.title("Laptop Shopping Assistant")

    st.markdown(
        """
        <p class="app-subtitle">
            AI-powered product guidance grounded in your catalog,
            policies, pricing, and inventory information.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if view == "Shop":
        render_shopping_view(api_root)
    elif view == "FAQ":
        render_faq_view(api_root)
    else:
        render_cart_view(api_root)


if __name__ == "__main__":
    main()