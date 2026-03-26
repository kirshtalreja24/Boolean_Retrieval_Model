import streamlit as st
from processor import InvertedIndex
from Queries import Queries

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Boolean IR System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

.stApp {
    background-color: #0d0d0d;
    color: #e8e3d5;
}

section[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #2a2a2a;
}

.stTextInput > div > div > input {
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 4px !important;
    color: #e8e3d5 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 2px rgba(200, 169, 110, 0.15) !important;
}

.stButton > button {
    background-color: #c8a96e !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.5rem !important;
    transition: background-color 0.2s ease !important;
}

.stButton > button:hover {
    background-color: #e0c080 !important;
}

[data-testid="metric-container"] {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 1rem;
}

.result-card {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #c8a96e;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-family: 'DM Mono', monospace;
    color: #e8e3d5;
}

.result-card span {
    color: #c8a96e;
    font-weight: 500;
}

.header-strip {
    background: linear-gradient(90deg, #c8a96e22, transparent);
    border-left: 3px solid #c8a96e;
    padding: 0.5rem 1rem;
    margin-bottom: 1.5rem;
    border-radius: 0 4px 4px 0;
}

.tag {
    display: inline-block;
    background-color: #c8a96e22;
    color: #c8a96e;
    border: 1px solid #c8a96e44;
    border-radius: 3px;
    padding: 0.1rem 0.4rem;
    font-size: 0.75rem;
    margin: 0.15rem;
    font-family: 'DM Mono', monospace;
}

hr {
    border-color: #2a2a2a !important;
}

.stAlert {
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Load system — built once, cached after that
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Building index — please wait...")
def load_system():
    ii = InvertedIndex()
    ii.documentProcessing()
    return ii, Queries(ii)

ii, qp = load_system()


# ─────────────────────────────────────────────
# Sidebar — query guide only
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📖 Query Guide")
    st.markdown("---")

    st.markdown("**Boolean Operators**")
    st.code("term1 AND term2\nterm1 OR term2\nNOT term1\nNOT (term1 OR term2)\n(a AND b) OR (c AND d)", language="text")

    st.markdown("**Phrase Query**")
    st.code('"new york"\n"air crash landing"', language="text")

    st.markdown("**Proximity Query**")
    st.code("united plane /3\ncrash land /2", language="text")
    st.caption("`t1 t2 /k` — t1 appears before t2 within k words")

    st.markdown("**Combined**")
    st.code('"air crash" AND NOT boeing\n(united OR delta) AND plane /2', language="text")


# ─────────────────────────────────────────────
# Main panel
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-strip">
    <h1 style="margin:0; font-size:1.8rem; color:#e8e3d5;">
        Boolean Information Retrieval
    </h1>
    <p style="margin:0.2rem 0 0; font-size:0.82rem; color:#888;">
        Positional Inverted Index &nbsp;·&nbsp; Boolean · Phrase · Proximity Queries
    </p>
</div>
""", unsafe_allow_html=True)

# Input row
col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        label="query",
        label_visibility="collapsed",
        placeholder='e.g.  "air crash"  |  united AND NOT plane  |  crash land /2',
        key="query_input",
    )
with col_btn:
    search_clicked = st.button("Search", use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Run query and show results
# ─────────────────────────────────────────────
if search_clicked and query.strip():
    try:
        results = qp.queryInput(query.strip())

        m1, m2 = st.columns(2)
        m1.metric("Documents Found", len(results))
        m2.metric("Documents Not Matched", len(qp.all_docs) - len(results))

        st.markdown("")

        if results:
            st.markdown("#### Matching Document IDs")
            tags_html = "".join(f'<span class="tag">doc {r}</span>' for r in results)
            st.markdown(tags_html, unsafe_allow_html=True)

            st.markdown("")

            with st.expander("Detailed Results", expanded=False):
                for i, doc_id in enumerate(results, 1):
                    st.markdown(
                        f'<div class="result-card"><span>#{i}</span> &nbsp; Document ID: <span>{doc_id}</span></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No documents matched your query. Try different terms or operators.")

    except ValueError as e:
        st.error(f"Query error: {e}")

elif search_clicked and not query.strip():
    st.warning("Please enter a query.")

else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0; color:#444;">
        <div style="font-size:3rem;">🔎</div>
        <p style="font-family:'Syne',sans-serif; font-size:1.1rem; margin-top:0.5rem;">
            Enter a query above to search the index.
        </p>
    </div>
    """, unsafe_allow_html=True)