import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Crash Analytics & Risk Management",
    page_icon="📈",
    layout="wide",
)

st.title("📈 لوحة تحليل ألعاب Crash وإدارة المخاطر")
st.markdown(
    "نظام تحليلي لمساعدة اللاعبين على تتبع البيانات وإدارة رأس المال بذكاء."
)

if "history" not in st.session_state:
    st.session_state.history = [
        1.20,
        2.50,
        1.15,
        4.10,
        1.05,
        1.85,
        1.30,
        12.00,
        1.10,
        1.95,
    ]

st.sidebar.header("⚙️ إعدادات الحساب وإدارة المخاطر")
bankroll = st.sidebar.number_input(
    "رأس المال الكلي (Bankroll):", min_value=10.0, value=1000.0, step=50.0
)
risk_pct = (
    st.sidebar.slider(
        "نسبة المخاطرة القصوى لكل جولة (%):",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.5,
    )
    / 100
)

st.sidebar.markdown("---")
st.sidebar.header("➕ إضافة نتيجة جولة جديدة")
new_val = st.sidebar.number_input(
    "المضاعف (Multiplier):", min_value=1.00, value=1.50, step=0.05
)

if st.sidebar.button("إضافة الجولة"):
    st.session_state.history.append(new_val)
    st.sidebar.success(f"تمت إضافة {new_val}x بنجاح!")

if st.sidebar.button("مسح جميع البيانات"):
    st.session_state.history = []
    st.sidebar.warning("تم مسح السجل!")

df = pd.Series(st.session_state.history)

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    total_rounds = len(df)
    mean_val = df.mean()
    median_val = df.median()
    under_1_5 = (df < 1.5).sum() / total_rounds * 100

    col1.metric("عدد الجولات المسجلة", total_rounds)
    col2.metric("متوسط المضاعف (Mean)", f"{mean_val:.2f}x")
    col3.metric("الوسيط الإحصائي (Median)", f"{median_val:.2f}x")
    col4.metric("نسبة السقوط أقل من 1.5x", f"{under_1_5:.1f}%")

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 مسار المضاعفات فـ الجولات الأخيرة")
        fig = px.line(
            x=list(range(1, total_rounds + 1)),
            y=df.values,
            labels={"x": "رقم الجولة", "y": "المضاعف (x)"},
            title="تتبع المنحنى الزمني",
        )
        fig.add_hline(
            y=1.5,
            line_dash="dash",
            line_color="red",
            annotation_text="منطقة خطر (1.5x)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🎯 حاسبة الرهان (Kelly Criterion)")
        target_mult = st.number_input(
            "المضاعف المستهدف:", min_value=1.1, value=2.0, step=0.1
        )
        estimated_prob = (
            st.slider(
                "نسبة النجاح المتوقعة (%):",
                min_value=10,
                max_value=90,
                value=45,
            )
            / 100
        )

        b = target_mult - 1
        p = estimated_prob
        q = 1 - p
        f = (b * p - q) / b if b > 0 else 0

        if f > 0:
            recommended_stake = bankroll * f * risk_pct
            st.success(f"الرهان الموصى به: **{recommended_stake:.2f} درهم**")
            st.caption(
                f"يمثل {((recommended_stake/bankroll)*100):.2f}% من رأس مالك."
            )
        else:
            st.error("⚠️ المخاطرة عالية جداً فـ هاد التوقع. ينصح بعدم الدخول!")

    st.subheader("📋 سجل النتائج")
    st.dataframe(
        pd.DataFrame(
            {"الجولة": list(range(1, total_rounds + 1)), "المضاعف": df.values}
        ).sort_index(ascending=False),
        use_container_width=True,
    )
else:
    st.info("قم بإضافة نتائج الجولات من القائمة الجانبية لبدء التحليل.")
