import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EduPro Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0d0d1a; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #12122b; border-right: 1px solid #2a2a5a; }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a3e, #2a1a4e);
        border: 1px solid #6a0dad;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="metric-container"] label { color: #c084fc !important; font-size: 0.78rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffd700 !important; font-size: 1.8rem !important; font-weight: 700; }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #6a0dad, #1a0050);
        color: #ffd700;
        padding: 10px 18px;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 16px 0 10px 0;
        letter-spacing: 0.5px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { background: #12122b; border-radius: 8px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { background: #1a1a3e; color: #c084fc; border-radius: 6px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background: #6a0dad; color: #ffd700; font-weight: 700; }

    /* Slider & select */
    .stSlider > div > div > div { background: #6a0dad; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #6a0dad; }

    /* Title */
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffd700;
        text-decoration: underline;
        margin-bottom: 4px;
    }
    .sub-title {
        text-align: center;
        color: #c084fc;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    
    /* Dataframe */
    .stDataFrame { border: 1px solid #6a0dad; border-radius: 8px; }
    
    /* Sidebar label */
    .sidebar-label {
        color: #ffd700;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY DARK THEME DEFAULTS
# ─────────────────────────────────────────────
PLOT_BG   = "#0d0d1a"
PAPER_BG  = "#12122b"
GRID_CLR  = "#2a2a5a"
FONT_CLR  = "#e0e0e0"
GOLD      = "#ffd700"
PURPLE    = "#6a0dad"
TEAL      = "#00d4aa"
ACCENT    = "#c084fc"

PLOTLY_LAYOUT = dict(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    font=dict(color=FONT_CLR, family="Arial"),
    xaxis=dict(gridcolor=GRID_CLR, color=FONT_CLR),
    yaxis=dict(gridcolor=GRID_CLR, color=FONT_CLR),
    legend=dict(bgcolor=PAPER_BG, bordercolor=PURPLE, borderwidth=1, font=dict(color=FONT_CLR)),
    margin=dict(l=40, r=20, t=50, b=40),
)

COLOR_SEQ = [TEAL, GOLD, PURPLE, ACCENT, "#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24",
             "#6c5ce7", "#fd79a8", "#00b894", "#e17055"]

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    path = "EduPro_Online_Platform__1___1_.xlsx"
    users    = pd.read_excel(path, sheet_name="Users")
    txns     = pd.read_excel(path, sheet_name="Transactions")
    courses  = pd.read_excel(path, sheet_name="Courses")
    teachers = pd.read_excel(path, sheet_name="Teachers")

    # Merge master
    master = txns.merge(courses,  on="CourseID",  how="left") \
                 .merge(teachers, on="TeacherID", how="left") \
                 .merge(users,    on="UserID",    how="left")

    # DAX-style calculated columns
    master["EnrollmentInfluenceRatio"] = master.groupby("TeacherID")["CourseID"].transform("count") / \
                                          master.groupby("TeacherID")["CourseID"].transform("nunique")

    exp_avg = teachers.groupby("YearsOfExperience")["TeacherRating"].mean()
    teachers["ExperienceImpactScore"] = teachers["YearsOfExperience"].map(
        lambda x: round(teachers["TeacherRating"].mean() / exp_avg.mean(), 2)
        if exp_avg.mean() != 0 else 1.0
    )
    teachers["RatingConsistencyIndex"] = (
        teachers["TeacherRating"] / teachers["TeacherRating"].max()
    ).round(2)

    def rating_tier(r):
        if r >= 4.0: return "Top"
        elif r >= 3.0: return "Average"
        else: return "Low"
    courses["RatingTier"] = courses["CourseRating"].apply(rating_tier)

    return users, txns, courses, teachers, master

users, txns, courses, teachers, master = load_data()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='text-align:center; color:#ffd700; font-size:1.3rem; font-weight:800; margin-bottom:16px;'>🎓 EduPro Filters</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-label'>📚 Course Category</div>", unsafe_allow_html=True)
    all_cats = sorted(courses["CourseCategory"].unique())
    sel_cats = st.multiselect("", all_cats, default=all_cats, key="cats", label_visibility="collapsed")

    st.markdown("<div class='sidebar-label'>🎯 Instructor Expertise</div>", unsafe_allow_html=True)
    all_exp = sorted(teachers["Expertise"].unique())
    sel_exp = st.multiselect("", all_exp, default=all_exp, key="exp", label_visibility="collapsed")

    st.markdown("<div class='sidebar-label'>📊 Course Level</div>", unsafe_allow_html=True)
    all_lvls = courses["CourseLevel"].unique().tolist()
    sel_lvls = st.multiselect("", all_lvls, default=all_lvls, key="lvls", label_visibility="collapsed")

    st.markdown("<div class='sidebar-label'>💳 Course Type</div>", unsafe_allow_html=True)
    sel_type = st.radio("", ["All", "Free", "Paid"], key="ctype", label_visibility="collapsed", horizontal=True)

    st.markdown("<div class='sidebar-label'>⭐ Teacher Rating Range</div>", unsafe_allow_html=True)
    t_min, t_max = float(teachers["TeacherRating"].min()), float(teachers["TeacherRating"].max())
    sel_rating = st.slider("", t_min, t_max, (t_min, t_max), step=0.1, key="trating", label_visibility="collapsed")

    st.markdown("<div class='sidebar-label'>🌟 Course Rating Range</div>", unsafe_allow_html=True)
    c_min, c_max = float(courses["CourseRating"].min()), float(courses["CourseRating"].max())
    sel_crating = st.slider("", c_min, c_max, (c_min, c_max), step=0.1, key="crating", label_visibility="collapsed")

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
filt_courses  = courses[
    (courses["CourseCategory"].isin(sel_cats)) &
    (courses["CourseLevel"].isin(sel_lvls)) &
    (courses["CourseRating"].between(*sel_crating))
]
if sel_type != "All":
    filt_courses = filt_courses[filt_courses["CourseType"] == sel_type]

filt_teachers = teachers[
    (teachers["Expertise"].isin(sel_exp)) &
    (teachers["TeacherRating"].between(*sel_rating))
]

filt_master = master[
    (master["CourseCategory"].isin(sel_cats)) &
    (master["CourseLevel"].isin(sel_lvls)) &
    (master["Expertise"].isin(sel_exp)) &
    (master["TeacherRating"].between(*sel_rating)) &
    (master["CourseRating"].between(*sel_crating))
]
if sel_type != "All":
    filt_master = filt_master[filt_master["CourseType"] == sel_type]

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.markdown("<div class='main-title'>🎓 EduPro – Instructor & Course Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Instructor Performance & Course Quality Evaluation | Unified Mentor Internship Project</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

avg_t_rating = round(filt_teachers["TeacherRating"].mean(), 2) if len(filt_teachers) else 0
avg_c_rating = round(filt_courses["CourseRating"].mean(), 2) if len(filt_courses) else 0
total_enroll = len(filt_master)
enroll_ratio = round(total_enroll / filt_teachers["TeacherID"].nunique(), 2) if filt_teachers["TeacherID"].nunique() > 0 else 0
exp_impact   = round(filt_teachers["ExperienceImpactScore"].mean(), 2) if len(filt_teachers) else 0
rci          = round(filt_teachers["RatingConsistencyIndex"].mean(), 2) if len(filt_teachers) else 0

k1.metric("⭐ Avg Teacher Rating",       f"{avg_t_rating}")
k2.metric("📘 Avg Course Rating",         f"{avg_c_rating}")
k3.metric("👥 Total Enrollments",         f"{total_enroll:,}")
k4.metric("📈 Enrollment Influence Ratio",f"{enroll_ratio}")
k5.metric("💡 Exp Impact Score",          f"{exp_impact}")

st.markdown("<hr style='border:1px solid #2a2a5a; margin:8px 0;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Instructor Leaderboard",
    "📊 Experience vs Rating",
    "🔥 Course Quality",
    "🎯 Expertise Analysis"
])

# ════════════════════════════════════════════
# TAB 1 — INSTRUCTOR LEADERBOARD
# ════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>🏆 Instructor Performance Leaderboard</div>", unsafe_allow_html=True)

    if len(filt_master) == 0:
        st.warning("No data with current filters.")
    else:
        # Aggregate per teacher
        t_agg = filt_master.groupby(["TeacherID", "TeacherName", "Expertise", "TeacherRating", "YearsOfExperience"]).agg(
            TotalEnrollments=("TransactionID", "count"),
            AvgCourseRating=("CourseRating", "mean"),
            UniqueCourses=("CourseID", "nunique"),
        ).reset_index()
        t_agg["AvgCourseRating"] = t_agg["AvgCourseRating"].round(2)

        def perf_tag(r):
            if r >= 4.0: return "🟢 Top Performer"
            elif r >= 3.0: return "🟡 Average"
            else: return "🔴 Low Performer"
        t_agg["Performance"] = t_agg["TeacherRating"].apply(perf_tag)

        c1, c2 = st.columns([2, 1])

        with c1:
            # Top 10 bar chart
            top10 = t_agg.nlargest(10, "TeacherRating").sort_values("TeacherRating")
            colors = [TEAL if r >= 4.0 else (GOLD if r >= 3.0 else "#ff6b6b") for r in top10["TeacherRating"]]
            fig = go.Figure(go.Bar(
                y=top10["TeacherName"], x=top10["TeacherRating"],
                orientation="h",
                marker_color=colors,
                text=top10["TeacherRating"], textposition="outside",
                textfont=dict(color=FONT_CLR, size=11),
                hovertemplate="<b>%{y}</b><br>Rating: %{x}<br>",
            ))
            fig.update_layout(**PLOTLY_LAYOUT, title=dict(text="Top 10 Teachers by Rating", font=dict(color=GOLD, size=14)),
                              height=380, xaxis_range=[0, 6])
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Rating distribution donut
            tier_counts = t_agg["Performance"].value_counts().reset_index()
            tier_counts.columns = ["Tier", "Count"]
            fig2 = px.pie(tier_counts, names="Tier", values="Count", hole=0.55,
                          color_discrete_sequence=[TEAL, GOLD, "#ff6b6b"])
            fig2.update_layout(**PLOTLY_LAYOUT, title=dict(text="Performance Distribution", font=dict(color=GOLD, size=14)), height=380)
            fig2.update_traces(textfont_color=FONT_CLR)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='section-header'>📋 Full Instructor Table</div>", unsafe_allow_html=True)
        disp = t_agg[["TeacherName","Expertise","TeacherRating","TotalEnrollments","AvgCourseRating","UniqueCourses","Performance"]].sort_values("TeacherRating", ascending=False)
        st.dataframe(disp.reset_index(drop=True), use_container_width=True, height=300)

        # Low Performers highlight
        st.markdown("<div class='section-header'>⚠️ Low Performers (Rating < 3.0)</div>", unsafe_allow_html=True)
        low = t_agg[t_agg["TeacherRating"] < 3.0].sort_values("TeacherRating")[["TeacherName","Expertise","TeacherRating","TotalEnrollments"]]
        if len(low) == 0:
            st.success("No low performers in current filter selection!")
        else:
            st.dataframe(low.reset_index(drop=True), use_container_width=True)

# ════════════════════════════════════════════
# TAB 2 — EXPERIENCE vs RATING SCATTER
# ════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>📊 Experience vs Rating Analysis</div>", unsafe_allow_html=True)

    if len(filt_master) == 0:
        st.warning("No data with current filters.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            # YearsOfExperience vs TeacherRating scatter
            fig = px.scatter(
                filt_teachers, x="YearsOfExperience", y="TeacherRating",
                color="Expertise", size_max=14,
                hover_name="TeacherName",
                hover_data={"Expertise": True, "TeacherRating": ":.2f", "YearsOfExperience": True},
                color_discrete_sequence=COLOR_SEQ,
                title="Years of Experience vs Teacher Rating",
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=400,
                              title=dict(text="Years of Experience vs Teacher Rating", font=dict(color=GOLD, size=13)))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Experience vs Course Rating (line aggregated)
            exp_course = filt_master.groupby("YearsOfExperience")["CourseRating"].mean().reset_index()
            exp_course.columns = ["YearsOfExperience", "AvgCourseRating"]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=exp_course["YearsOfExperience"], y=exp_course["AvgCourseRating"].round(2),
                mode="lines+markers+text",
                line=dict(color=TEAL, width=2.5),
                marker=dict(size=7, color=GOLD),
                text=exp_course["AvgCourseRating"].round(2),
                textposition="top center",
                textfont=dict(color=FONT_CLR, size=9),
                name="Avg Course Rating"
            ))
            fig2.update_layout(**PLOTLY_LAYOUT, height=400,
                               title=dict(text="Years of Experience vs Avg Course Rating", font=dict(color=GOLD, size=13)),
                               xaxis_title="Years of Experience", yaxis_title="Avg Course Rating")
            st.plotly_chart(fig2, use_container_width=True)

        # Age distribution
        st.markdown("<div class='section-header'>👤 Instructor Age Distribution</div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)

        with c3:
            age_bins = filt_teachers.copy()
            age_bins["AgeGroup"] = pd.cut(age_bins["Age"], bins=[25,30,35,40,45,50,55], labels=["26-30","31-35","36-40","41-45","46-50","51-55"])
            age_cnt = age_bins.groupby("AgeGroup", observed=True).size().reset_index(name="Count")
            fig3 = px.bar(age_cnt, x="AgeGroup", y="Count", color="Count",
                          color_continuous_scale=["#6a0dad", TEAL])
            fig3.update_layout(**PLOTLY_LAYOUT, height=340,
                               title=dict(text="Instructor Age Distribution", font=dict(color=GOLD, size=13)),
                               coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            # Bubble: Experience vs Rating sized by enrollment
            t_enroll = filt_master.groupby("TeacherID")["TransactionID"].count().reset_index(name="Enrollments")
            bubble_df = filt_teachers.merge(t_enroll, on="TeacherID", how="left").fillna(0)
            fig4 = px.scatter(bubble_df, x="YearsOfExperience", y="TeacherRating",
                              size="Enrollments", color="Expertise",
                              hover_name="TeacherName",
                              size_max=40,
                              color_discrete_sequence=COLOR_SEQ)
            fig4.update_layout(**PLOTLY_LAYOUT, height=340,
                               title=dict(text="Bubble: Exp vs Rating (size=Enrollments)", font=dict(color=GOLD, size=13)))
            st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════
# TAB 3 — COURSE QUALITY HEATMAPS
# ════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>🔥 Course Quality Evaluation</div>", unsafe_allow_html=True)

    if len(filt_courses) == 0:
        st.warning("No courses with current filters.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            # Heatmap: Category vs Level avg course rating
            heat_df = filt_courses.groupby(["CourseCategory", "CourseLevel"])["CourseRating"].mean().round(2).reset_index()
            heat_pivot = heat_df.pivot(index="CourseCategory", columns="CourseLevel", values="CourseRating")
            fig = px.imshow(
                heat_pivot, text_auto=True,
                color_continuous_scale=["#1a0050", PURPLE, TEAL, GOLD],
                aspect="auto",
                title="Course Rating Heatmap (Category × Level)"
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=420,
                              title=dict(text="Course Rating Heatmap (Category × Level)", font=dict(color=GOLD, size=13)))
            fig.update_coloraxes(colorbar=dict(tickfont=dict(color=FONT_CLR), title=dict(font=dict(color=FONT_CLR))))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Free vs Paid by Level
            fp_df = filt_courses.groupby(["CourseType","CourseLevel"])["CourseRating"].mean().round(2).reset_index()
            fig2 = px.bar(fp_df, x="CourseLevel", y="CourseRating", color="CourseType",
                          barmode="group", text="CourseRating",
                          color_discrete_map={"Free": TEAL, "Paid": GOLD},
                          title="Free vs Paid — Avg Rating by Level")
            fig2.update_traces(textposition="outside", textfont=dict(color=FONT_CLR, size=10))
            fig2.update_layout(**PLOTLY_LAYOUT, height=420,
                               title=dict(text="Free vs Paid — Avg Rating by Level", font=dict(color=GOLD, size=13)),
                               yaxis_range=[0, 6])
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='section-header'>⏱️ Duration vs Rating & Enrollment Trends</div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)

        with c3:
            # Duration vs Rating scatter
            fig3 = px.scatter(filt_courses, x="CourseDuration", y="CourseRating",
                              color="CourseCategory", hover_name="CourseName",
                              color_discrete_sequence=COLOR_SEQ,
                              )
            fig3.update_layout(**PLOTLY_LAYOUT, height=360,
                               title=dict(text="Course Duration vs Rating", font=dict(color=GOLD, size=13)),
                               xaxis_title="Duration (hrs)", yaxis_title="Course Rating")
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            # Enrollment by category
            enroll_cat = filt_master.groupby("CourseCategory")["TransactionID"].count().reset_index(name="Enrollments").sort_values("Enrollments", ascending=False)
            fig4 = px.bar(enroll_cat, x="CourseCategory", y="Enrollments",
                          text="Enrollments", color="Enrollments",
                          color_continuous_scale=["#6a0dad", TEAL])
            fig4.update_traces(textposition="outside", textfont=dict(color=FONT_CLR, size=9))
            fig4.update_layout(**PLOTLY_LAYOUT, height=360,
                               title=dict(text="Enrollments by Course Category", font=dict(color=GOLD, size=13)),
                               coloraxis_showscale=False, xaxis_tickangle=-35)
            st.plotly_chart(fig4, use_container_width=True)

        # Rating Tier donut
        st.markdown("<div class='section-header'>🎖️ Course Rating Tier Distribution</div>", unsafe_allow_html=True)
        tier_df = filt_courses["RatingTier"].value_counts().reset_index()
        tier_df.columns = ["Tier", "Count"]
        fig5 = px.pie(tier_df, names="Tier", values="Count", hole=0.5,
                      color_discrete_map={"Top": TEAL, "Average": GOLD, "Low": "#ff6b6b"})
        fig5.update_layout(**PLOTLY_LAYOUT, height=320,
                           title=dict(text="Rating Tier Breakdown", font=dict(color=GOLD, size=13)))
        fig5.update_traces(textfont_color=FONT_CLR)
        st.plotly_chart(fig5, use_container_width=True)

# ════════════════════════════════════════════
# TAB 4 — EXPERTISE ANALYSIS
# ════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>🎯 Expertise-wise Performance Comparison</div>", unsafe_allow_html=True)

    if len(filt_master) == 0:
        st.warning("No data with current filters.")
    else:
        # Expertise gaps bar
        exp_perf = filt_master.groupby("Expertise").agg(
            AvgTeacherRating=("TeacherRating", "mean"),
            AvgCourseRating=("CourseRating", "mean"),
            TotalEnrollments=("TransactionID", "count"),
        ).reset_index()
        exp_perf = exp_perf.sort_values("AvgTeacherRating", ascending=False)
        exp_perf[["AvgTeacherRating","AvgCourseRating"]] = exp_perf[["AvgTeacherRating","AvgCourseRating"]].round(2)

        overall_avg = round(filt_teachers["TeacherRating"].mean(), 2)

        c1, c2 = st.columns(2)

        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=exp_perf["Expertise"], y=exp_perf["AvgTeacherRating"],
                name="Avg Teacher Rating",
                marker_color=[TEAL if v >= overall_avg else "#ff6b6b" for v in exp_perf["AvgTeacherRating"]],
                text=exp_perf["AvgTeacherRating"], textposition="outside",
                textfont=dict(color=FONT_CLR, size=9),
            ))
            fig.add_hline(y=overall_avg, line_dash="dot", line_color=GOLD,
                          annotation_text=f"Avg: {overall_avg}", annotation_font_color=GOLD)
            fig.update_layout(**PLOTLY_LAYOUT, height=400,
                              title=dict(text="Expertise Gaps (Teacher Rating vs Avg)", font=dict(color=GOLD, size=13)),
                              xaxis_tickangle=-35, yaxis_range=[0, 6])
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Radar chart: multi-metric per expertise
            categories = exp_perf["Expertise"].tolist()
            norm_tr = exp_perf["AvgTeacherRating"] / 5
            norm_cr = exp_perf["AvgCourseRating"] / 5
            norm_en = exp_perf["TotalEnrollments"] / exp_perf["TotalEnrollments"].max()

            fig2 = go.Figure()
            for i, row in exp_perf.iterrows():
                fig2.add_trace(go.Scatterpolar(
                    r=[row["AvgTeacherRating"]/5, row["AvgCourseRating"]/5,
                       row["TotalEnrollments"]/exp_perf["TotalEnrollments"].max()],
                    theta=["Teacher Rating", "Course Rating", "Enrollments"],
                    name=row["Expertise"],
                    fill="toself",
                    opacity=0.6,
                ))
            fig2.update_layout(
                polar=dict(
                    bgcolor=PLOT_BG,
                    radialaxis=dict(visible=True, gridcolor=GRID_CLR, color=FONT_CLR, range=[0,1]),
                    angularaxis=dict(gridcolor=GRID_CLR, color=FONT_CLR)
                ),
                paper_bgcolor=PAPER_BG,
                font=dict(color=FONT_CLR),
                height=400,
                title=dict(text="Radar: Multi-Metric per Expertise", font=dict(color=GOLD, size=13)),
                showlegend=True,
                legend=dict(bgcolor=PAPER_BG, bordercolor=PURPLE, font=dict(color=FONT_CLR, size=8)),
                margin=dict(l=40, r=40, t=50, b=40),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='section-header'>📊 Teacher vs Course Rating by Expertise</div>", unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=exp_perf["Expertise"], y=exp_perf["AvgTeacherRating"],
            name="Avg Teacher Rating", marker_color=PURPLE,
            text=exp_perf["AvgTeacherRating"], textposition="outside",
            textfont=dict(color=FONT_CLR, size=9),
        ))
        fig3.add_trace(go.Bar(
            x=exp_perf["Expertise"], y=exp_perf["AvgCourseRating"],
            name="Avg Course Rating", marker_color=TEAL,
            text=exp_perf["AvgCourseRating"], textposition="outside",
            textfont=dict(color=FONT_CLR, size=9),
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, barmode="group", height=380,
                           title=dict(text="Teacher Rating vs Course Rating by Expertise", font=dict(color=GOLD, size=13)),
                           xaxis_tickangle=-30, yaxis_range=[0, 6])
        st.plotly_chart(fig3, use_container_width=True)

        # Gender split per expertise
        st.markdown("<div class='section-header'>⚧️ Gender Distribution by Expertise</div>", unsafe_allow_html=True)
        gen_exp = filt_master.groupby(["Expertise", "Gender_y"])["TransactionID"].count().reset_index(name="Count")
        gen_exp.columns = ["Expertise", "Gender", "Count"]
        fig4 = px.bar(gen_exp, x="Expertise", y="Count", color="Gender",
                      barmode="stack", color_discrete_map={"Male": "#4fc3f7", "Female": "#f48fb1"})
        fig4.update_layout(**PLOTLY_LAYOUT, height=360,
                           title=dict(text="Enrollments by Expertise & Gender", font=dict(color=GOLD, size=13)),
                           xaxis_tickangle=-30)
        st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<hr style='border:1px solid #2a2a5a; margin:24px 0 8px 0;'>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#6a6a9a; font-size:0.8rem; padding-bottom:10px;'>
    🎓 EduPro Analytics Dashboard &nbsp;|&nbsp; Unified Mentor Internship Project &nbsp;|&nbsp; Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
