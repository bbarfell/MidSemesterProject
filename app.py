import streamlit as st
import json
import uuid
import time
from pathlib import Path

USER_FILE = Path("shop_users.json")
CATALOG_FILE = Path("flower_catalog.json")

def load_json(path, default_data):
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return default_data

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

initial_users = [
    {"id": "1", "email": "admin@petals.com", "password": "admin", "role": "Admin"},
    {"id": "2", "email": "florist@petals.com", "password": "staff", "role": "Florist"},
    {"id": "3", "email": "customer@gmail.com", "password": "user123", "role": "Customer"}
]

users = load_json(USER_FILE, initial_users)
catalog = load_json(CATALOG_FILE, [
    {"id": "F1", "name": "Midnight Rose", "price": 55.0, "stock": 10},
    {"id": "F2", "name": "Sunny Daisy", "price": 25.0, "stock": 15}
])

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "user": None, "role": None, "cart": []})

st.set_page_config(page_title="Petals & Blooms", layout="centered", page_icon="")



if not st.session_state["logged_in"]:
    st.title("Petals & Blooms Boutique")
    auth_tab, reg_tab = st.tabs(["Sign In", "Create Account"])

    with auth_tab:
        with st.form("login_form"):
            email_in = st.text_input("Email").strip().lower()
            pass_in = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Log In", use_container_width=True)

            if submit_login:
                found_user = next((u for u in users if u["email"].lower() == email_in and u["password"] == pass_in), None)
                if found_user:
                    st.session_state.update({"logged_in": True, "user": found_user, "role": found_user["role"]})
                    st.success(f"Welcome back, {found_user['role']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Account not found or password incorrect.")

    with reg_tab:
        st.subheader("Join our Flower Club")
        with st.form("reg_form"):
            new_email = st.text_input("Email Address")
            new_pass = st.text_input("Choose Password", type="password")
            role_choice = st.radio("Account Type", ["Customer", "Florist"], horizontal=True)
            submit_reg = st.form_submit_button("Register Now")

            if submit_reg:
                if any(u['email'] == new_email.lower() for u in users):
                    st.warning("That email is already registered.")
                elif new_email and new_pass:
                    new_user = {
                        "id": str(uuid.uuid4())[:8],
                        "email": new_email.lower(),
                        "password": new_pass,
                        "role": role_choice
                    }
                    users.append(new_user)
                    save_json(USER_FILE, users)
                    st.success("Account created! You can now Sign In.")
                else:
                    st.error("Please fill in all fields.")
    
    st.stop()


with st.sidebar:
    st.title("Petals & Blooms")
    st.write(f"Logged in as: **{st.session_state['user']['email']}**")
    st.caption(f"Access Level: {st.session_state['role']}")
    if st.button("Log Out"):
        st.session_state.update({"logged_in": False, "user": None, "role": None, "cart": []})
        st.rerun()


# CUSTOMER VIEW 
if st.session_state["role"] == "Customer":
    st.title("Shop Our Collection")
    st.write("Browse our fresh arrangements and place your order.")
    
    cols = st.columns(2)
    for i, item in enumerate(catalog):
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(item['name'])
                st.write(f"Price: **${item['price']:.2f}**")
                st.write(f"In Stock: {item['stock']}")
                if st.button(f"Add {item['name']} to Cart", key=f"buy_{item['id']}"):
                    st.session_state.cart.append(item['name'])
                    st.toast(f"Added {item['name']} to cart!")

    if st.session_state.cart:
        with st.sidebar:
            st.divider()
            st.subheader("Your Cart")
            for item in st.session_state.cart:
                st.write(f"• {item}")
            if st.button("Checkout"):
                st.balloons()
                st.success("Order Placed!")
                st.session_state.cart = []

# FLORIST / ADMIN VIEW 
elif st.session_state["role"] in ["Florist", "Admin"]:
    st.title("Shop Management")
    
    m_tab1, m_tab2 = st.tabs(["Manage Inventory", "Staff Logs"])
    
    with m_tab1:
        st.subheader("Inventory Control")
        edited_df = st.data_editor(catalog, num_rows="dynamic", key="catalog_editor")
        if st.button("Save Inventory Changes"):
            save_json(CATALOG_FILE, edited_df)
            st.success("Catalog updated!")

    with m_tab2:
        if st.session_state["role"] == "Admin":
            st.subheader("User Database")
            st.table(users)
        else:
            st.info("Staff members can view stock, but only Admins see user data.")


if st.session_state["role"] == "Admin":
    st.divider()
    st.subheader("Admin System Logs")
    st.json(users)


json_file = Path("flower_inventory.json")

def save_data(data):
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)

if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    inventory = [
        {"name": "Red Roses", "price": 45.00, "stock": 50},
        {"name": "Sunflowers", "price": 15.00, "stock": 30},
        {"name": "White Lilies", "price": 25.00, "stock": 20},
        {"name": "Tulip Bouquet", "price": 35.00, "stock": 15}
    ]
    save_data(inventory)

if "orders" not in st.session_state:
    st.session_state.orders = []

# Page Configuration
st.set_page_config(page_title="Petals & Blooms Flower Shop", layout="wide", page_icon="")
st.title(" Petals & Blooms Flower Shop")

tabs = st.tabs(["Create Bouquet", "Inventory View", "Restock Flowers", "Order Tracking"])

# SECTION 1: Place Order
with tabs[0]:
    st.header("Place a New Floral Order")
    
    col1, col2 = st.columns(2)
    with col1:
        item_names = [item["name"] for item in inventory]
        selected_name = st.selectbox("Select Flower or Bouquet", item_names)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        customer_name = st.text_input("Customer Name")
        
        # Find item details
        item_data = next(item for item in inventory if item["name"] == selected_name)
        
        if st.button("Complete Purchase"):
            if not customer_name:
                st.error("Please enter a customer name for the delivery.")
            elif item_data["stock"] < quantity:
                st.error(f"Insufficient stock! Only {item_data['stock']} stems/bouquets remaining.")
            else:
                # Update inventory
                item_data["stock"] -= quantity
                save_data(inventory)

                total_price = item_data["price"] * quantity
                new_order = {
                    "order_id": str(uuid.uuid4())[:8].upper(),
                    "customer": customer_name,
                    "item": selected_name,
                    "quantity": quantity,
                    "total": total_price,
                    "status": "Processing"
                }
                st.session_state.orders.append(new_order)

                st.success("Order confirmed! Your flowers are being prepared.")
                with st.expander("Print Digital Receipt"):
                    st.write(f"**Order ID:** {new_order['order_id']}")
                    st.write(f"**Customer:** {new_order['customer']}")
                    st.write(f"**Floral Selection:** {new_order['item']} (x{quantity})")
                    st.write(f"**Total Amount:** ${total_price:.2f}")

with tabs[1]:
    st.header("Flower Stock Status")
    
    search = st.text_input("Search for a flower variety...", "").lower()
    total_stock = sum(item["stock"] for item in inventory)
    st.metric("Total Stems in Inventory", total_stock)
    
    filtered_inventory = [i for i in inventory if search in i["name"].lower()]

    for item in filtered_inventory:
        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            st.write(f"**{item['name']}**")
        with col_b:
            st.write(f"${item['price']:.2f} per unit")
        with col_c:
            if item["stock"] < 5:
                st.write(f" :red[{item['stock']} left (Low Stock)]")
            else:
                st.write(f" {item['stock']} in stock")
        st.divider()

with tabs[2]:
    st.header("New Shipment Arrival")
    
    restock_item = st.selectbox("Select Item to Restock", [i["name"] for i in inventory])
    add_amount = st.number_input("Stems/Bouquets Received", min_value=1, step=1)
    
    if st.button("Update Inventory"):
        for item in inventory:
            if item["name"] == restock_item:
                item["stock"] += add_amount
                break
        save_data(inventory)
        st.success(f"Inventory updated for {restock_item}.")

with tabs[3]:
    st.header("Active Deliveries & Pickups")
    
    if not st.session_state.orders:
        st.info("No active flower orders at the moment.")
    else:
        for order in st.session_state.orders:
            if order["status"] == "Processing":
                col_x, col_y = st.columns([3, 1])
                
                with col_x:
                    st.write(f"**Order ID: {order['order_id']}** — {order['customer']}")
                    st.write(f"Items: {order['quantity']}x {order['item']}")
                
                with col_y:
                    if st.button("Cancel Order", key=order["order_id"]):
                        # Refund stock
                        for item in inventory:
                            if item["name"] == order["item"]:
                                item["stock"] += order["quantity"]
                        save_data(inventory)
                        order["status"] = "Cancelled"
                        st.warning("Order cancelled and flowers returned to stock.")
                        st.rerun()
                
                st.divider()