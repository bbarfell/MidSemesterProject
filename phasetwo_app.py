import streamlit as st
from data import DataManager
from service import ShopService, AIChatAssistant

# Instantiate the Service Layer in Session State
if "shop" not in st.session_state:
    st.session_state.shop = ShopService()

def main():
    st.set_page_config(page_title="Petals & Blooms Phase 2", layout="wide")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        render_login_page()
    else:
        render_main_app()

def render_login_page():
    """Polished login screen with mandatory test account display."""
    st.title("🌷 Petals & Blooms Boutique")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("login_form"):
            st.subheader("Sign In")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Log In", use_container_width=True):
                user_data = st.session_state.shop.validate_login(email, password)
                if user_data:
                    st.session_state.update({"logged_in": True, "user": user_data})
                    st.rerun() # Addressing Phase 1 stale UI issues
                else:
                    st.error("Invalid credentials.")

    with col2:
        # Required Phase 2 Component: Test Accounts
        st.info("### Test Accounts\n"
                "**Admin:** admin@petals.com | admin\n"
                "**Florist:** florist@petals.com | staff\n"
                "**Customer:** customer@gmail.com | user123")

def render_main_app():
    """Main app layout using Sidebar navigation and Dashboard sections."""
    user = st.session_state.user
    shop = st.session_state.shop
    
    with st.sidebar:
        st.title("Dashboard")
        st.write(f"User: **{user['role']}**")
        if st.button("Log Out"):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        st.subheader("Floral AI Assistant")
        user_query = st.text_input("Ask for bouquet care tips:")
        if user_query:
            api_key = st.secrets.get("OPENAI_API_KEY") # Recommended for Phase 2
            if api_key:
                assistant = AIChatAssistant(api_key)
                st.info(assistant.get_floral_advice(user_query))
            else:
                st.warning("Please configure OpenAI API Key in secrets.")

    # Role-Based Routing
    if user['role'] == "Customer":
        render_customer_view(shop)
    elif user['role'] in ["Florist", "Admin"]:
        render_staff_view(shop, user['role'])

def render_customer_view(shop):
    st.header("Shop Our Arrangements")
    tab1, tab2 = st.tabs(["Browse Collection", "My Orders"])
    
    with tab1:
        cols = st.columns(2)
        for idx, item in enumerate(shop.inventory):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(item['name'])
                    st.write(f"**Price:** ${item['price']:.2f}")
                    st.write(f"**Stock:** {item['stock']}")
                    if st.button(f"Order {item['name']}", key=f"buy_{idx}"):
                        if shop.process_purchase(item['name'], 1):
                            st.success(f"Ordered {item['name']}!")
                            st.rerun()
                        else:
                            st.error("Out of stock!")

def render_staff_view(shop, role):
    st.header(f"{role} Management Console")
    
    # Phase 2: CRUD using data_editor instead of raw dictionaries
    st.subheader("Inventory Control")
    edited_data = st.data_editor(shop.inventory, num_rows="dynamic", use_container_width=True)
    
    if st.button("Save Changes"):
        shop.inventory = edited_data
        DataManager.save(shop.inv_path, edited_data)
        st.success("Inventory updated and saved to JSON.")

if __name__ == "__main__":
    main()