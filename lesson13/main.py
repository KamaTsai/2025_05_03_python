import streamlit as st

def main():
    st.set_page_config(
        page_title="Streamlit App 首頁",
        page_icon="👋",
    )
    st.title("歡迎來到我的多頁面應用程式！")
    st.sidebar.success("請從上方選擇一個頁面。")

if __name__ == "__main__":
    main()