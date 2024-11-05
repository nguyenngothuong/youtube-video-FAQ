import streamlit as st
from supabase import create_client, Client
import re

class SupabaseAuth:
    def __init__(self):
        self.supabase: Client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["anon_key"]
        )
        
        # Khởi tạo session state cho auth
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None

    def validate_email(self, email: str) -> bool:
        """Kiểm tra email hợp lệ"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def validate_password(self, password: str) -> bool:
        """Kiểm tra mật khẩu hợp lệ (ít nhất 6 ký tự)"""
        return len(password) >= 6

    def sign_up(self, email: str, password: str) -> tuple[bool, str]:
        """Đăng ký tài khoản mới"""
        try:
            if not self.validate_email(email):
                return False, "Email không hợp lệ"
            if not self.validate_password(password):
                return False, "Mật khẩu phải có ít nhất 6 ký tự"

            data = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            return True, "Đăng ký thành công! Vui lòng kiểm tra email để kích hoạt tài khoản."
        except Exception as e:
            error_message = str(e)
            if "not authorized" in error_message.lower():
                return False, "Email này không được phép đăng ký. Vui lòng liên hệ admin hoặc sử dụng email khác."
            elif "already registered" in error_message.lower():
                return False, "Email này đã được đăng ký. Vui lòng sử dụng email khác hoặc đăng nhập."
            else:
                return False, f"Lỗi đăng ký: {error_message}"

    def sign_in(self, email: str, password: str) -> tuple[bool, str]:
        """Đăng nhập"""
        try:
            data = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            st.session_state.authenticated = True
            st.session_state.user = data.user
            return True, "Đăng nhập thành công!"
        except Exception as e:
            return False, f"Lỗi đăng nhập: {str(e)}"

    def sign_out(self):
        """Đăng xuất"""
        try:
            self.supabase.auth.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            return True, "Đã đăng xuất"
        except Exception as e:
            return False, f"Lỗi đăng xuất: {str(e)}"

    def render_auth_ui(self):
        """Hiển thị giao diện đăng nhập/đăng ký"""
        st.title("🔐 Xác thực người dùng")
        
        tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Mật khẩu", type="password", key="login_password")
                submit = st.form_submit_button("Đăng nhập")
                
                if submit:
                    success, message = self.sign_in(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        with tab2:
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Mật khẩu", type="password", key="signup_password")
                confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
                submit = st.form_submit_button("Đăng ký")
                
                if submit:
                    if password != confirm_password:
                        st.error("Mật khẩu xác nhận không khớp!")
                    else:
                        success, message = self.sign_up(email, password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message) 