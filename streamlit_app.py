import streamlit as st
from src.auth.supabase_auth import SupabaseAuth
from src.ui.main_app import MainApp

# Cấu hình trang
st.set_page_config(
    page_title="YouTube Playlist Transcript Extractor",
    page_icon="📝",
    layout="wide"
)

# Khởi tạo auth và main app
auth = SupabaseAuth()
app = MainApp()

# Kiểm tra xác thực
if not st.session_state.authenticated:
    auth.render_auth_ui()
else:
    # Hiển thị nút đăng xuất
    if st.sidebar.button("📤 Đăng xuất"):
        success, message = auth.sign_out()
        if success:
            st.rerun()
        else:
            st.sidebar.error(message)
    
    # Hiển thị thông tin người dùng
    st.sidebar.info(f"👤 Đang đăng nhập với: {st.session_state.user.email}")
    
    # Hiển thị ứng dụng chính
    app.render()