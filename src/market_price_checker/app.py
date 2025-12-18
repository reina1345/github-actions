import streamlit as st
import asyncio
from market_price_checker.scrapers import search_all

st.set_page_config(page_title="Market Price Checker", layout="wide")

st.title("市場価格調査ツール (Market Price Checker)")

st.sidebar.header("検索設定")
keyword = st.sidebar.text_input("検索キーワード", "")

if st.sidebar.button("検索開始"):
    if not keyword:
        st.error("キーワードを入力してください。")
    else:
        st.info(f"「{keyword}」の価格を調査中...")

        # Run async search
        results = asyncio.run(search_all(keyword))

        if not results:
            st.warning("商品が見つかりませんでした。")
        else:
            st.success(f"{len(results)} 件の商品が見つかりました。")

            # Convert to DataFrame for easier display if needed, or just iterate
            # For simplicity, display as cards or table

            # Simple table view
            st.dataframe(results)

            # Detailed view
            for res in results:
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.write(res['site'])
                    with col2:
                        st.markdown(f"**[{res['title']}]({res['url']})**")
                        st.write(f"価格: {res['price']} 円")
                    st.divider()
