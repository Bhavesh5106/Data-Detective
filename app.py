import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Data Detective", page_icon="🕵️", layout="wide", initial_sidebar_state="collapsed")

# ----------------------------- THEME ---------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp {
  background: radial-gradient(circle at 10% 5%, #ffe7a8 0, transparent 24%),
              radial-gradient(circle at 90% 15%, #d8c5ff 0, transparent 27%),
              linear-gradient(135deg, #fff7e8 0%, #f4f0ff 48%, #e8fbff 100%);
}
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1200px; }
h1,h2,h3 { font-family: 'Baloo 2', cursive !important; color: #28204d; }
.hero {
  background: linear-gradient(115deg,#4b35a8,#7957df 55%,#ec68a7);
  border-radius: 26px; padding: 28px 32px; color: white;
  box-shadow: 0 12px 30px #4932a533; margin-bottom: 18px;
}
.hero h1 { color:white !important; font-size: 3.1rem; margin:0; line-height:1.05; }
.hero p { color:#f5efff; font-size:1.08rem; margin:.45rem 0 0; }
.pill { display:inline-block; background:#fff2b8; color:#513b00; padding:6px 13px; border-radius:99px; font-weight:900; font-size:.8rem; margin:3px 5px 3px 0; }
.card {
 background:rgba(255,255,255,.88); border:1px solid #e7defc; border-radius:20px;
 padding:18px 20px; box-shadow:0 7px 20px #37236b0d; margin:8px 0 14px;
}
.level-card {
 background:white; border:2px solid #e9e2fa; border-radius:18px; padding:15px;
 min-height:140px; box-shadow:0 6px 18px #34205c10;
}
.level-card.active { border-color:#7657df; background:#f5f0ff; }
.level-card.done { border-color:#27b58a; background:#edfff8; }
.small-muted { color:#716b83; font-size:.92rem; }
.big-stat { font-family:'Baloo 2'; font-size:1.8rem; color:#4d36a7; font-weight:800; }
div.stButton > button {
 border:0; border-radius:13px; font-weight:900; padding:.62rem 1.1rem;
 background:linear-gradient(100deg,#6446cf,#ec65a7); color:white;
 box-shadow:0 5px 14px #7655d733;
}
div.stButton > button:hover { border:0; color:white; transform:translateY(-1px); }
div[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#24c6a1,#8b63ed,#ef6aa7); }
div[data-testid="stMetric"] { background:white; border:1px solid #e9e2fa; padding:12px; border-radius:16px; }
div[data-testid="stAlert"] { border-radius:15px; }
.character {
 background:white; border:2px solid #e9e2fa; border-radius:18px; padding:12px;
 text-align:center; min-height:120px;
}
.character.selected { border-color:#7657df; background:#f4efff; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ----------------------------- GAME DATA ----------------------------
CHARACTERS = {
    "Nova": ("🧑‍🚀", "The curious explorer", "Bonus hint on every case"),
    "Pixel": ("🤖", "The pattern-finding bot", "Starts each case with +5 XP"),
    "Sherlock": ("🕵️", "The classic investigator", "The detail detective"),
    "Zara": ("🧙‍♀️", "The data magician", "Turns tricky clues into insight"),
}

LEVELS = [
    ("01", "The Missing Clue", "🧩", "Clean the messy temperature records", "Missing values"),
    ("02", "The Suspicious Delivery", "📦", "Find the unusual delivery time", "Outlier detection"),
    ("03", "The Study Secret", "📚", "Discover the pattern in study data", "Correlation"),
    ("04", "The Biased Survey", "🗳️", "Check whether the sample is fair", "Sampling bias"),
    ("05", "The Ice-Cream Mystery", "🍦", "Separate a coincidence from a cause", "Correlation vs causation"),
]

def init_state():
    defaults = {
        "character": None, "unlocked": 1, "completed": [], "xp": 0,
        "answers": {}, "hints_used": [], "page": "home"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def award(level, points):
    key = str(level)
    if key not in st.session_state.completed:
        st.session_state.completed.append(key)
        st.session_state.xp += points
        st.session_state.unlocked = min(5, max(st.session_state.unlocked, level + 1))

def level_header(level):
    number, title, emoji, subtitle, concept = LEVELS[level-1]
    st.markdown(f'<div class="card"><span class="pill">CASE {number}</span><span class="pill">{concept.upper()}</span><h2 style="margin:8px 0 0">{emoji} {title}</h2><div class="small-muted">{subtitle}</div></div>', unsafe_allow_html=True)

def show_progress():
    done = len(st.session_state.completed)
    st.progress(done / 5, text=f"Case files solved: {done}/5")
    a,b,c = st.columns(3)
    a.metric("⭐ Detective XP", st.session_state.xp)
    b.metric("🗂️ Cases solved", f"{done}/5")
    c.metric("🔓 Cases unlocked", f"{st.session_state.unlocked}/5")

def finish_case(level, correct, explanation):
    if correct:
        award(level, 100 if str(level) not in st.session_state.hints_used else 70)
        st.success("Case solved! +100 XP" if str(level) not in st.session_state.hints_used else "Case solved! +70 XP (hint used)")
    else:
        st.error("Not quite! Review the evidence and try again.")
    st.info(explanation)

# ----------------------------- TOP BAR ------------------------------
st.markdown('<div class="hero"><div class="pill">A PLAY-TO-LEARN DATA SCIENCE GAME</div><h1>🕵️ DATA DETECTIVE</h1><p>Five mysteries. Real datasets. Your decisions reveal the science behind the clues.</p></div>', unsafe_allow_html=True)

if st.session_state.character:
    emoji, role, perk = CHARACTERS[st.session_state.character]
    left, right = st.columns([3,1])
    with left:
        st.markdown(f"**Detective:** {emoji} {st.session_state.character} · {role}")
    with right:
        st.markdown(f"**⭐ {st.session_state.xp} XP**")
    show_progress()

# ----------------------------- HOME ----------------------------------
if st.session_state.character is None or st.session_state.page == "home":
    st.markdown("## Choose your detective")
    st.write("Pick a character to lead the investigation. No data science experience needed!")
    cols = st.columns(4)
    for i, (name, details) in enumerate(CHARACTERS.items()):
        emoji, role, perk = details
        with cols[i]:
            st.markdown(f'<div class="character"><div style="font-size:2.5rem">{emoji}</div><b>{name}</b><br><span class="small-muted">{role}</span></div>', unsafe_allow_html=True)
            if st.button(f"Choose {name}", key=f"char_{name}", use_container_width=True):
                st.session_state.character = name
                st.session_state.page = "map"
                st.rerun()
    st.markdown('<div class="card"><h3>🎮 How to play</h3>1. Choose your detective.<br>2. Open the next unlocked case.<br>3. Inspect the evidence, make a decision and submit it.<br>4. Learn from the result, earn XP and unlock the next case.<br><br><b>Goal:</b> Solve all five cases and become a Data Detective!</div>', unsafe_allow_html=True)
    st.stop()

# ----------------------------- NAVIGATION ----------------------------
nav1, nav2 = st.columns([1,5])
with nav1:
    if st.button("🏠 Case map"):
        st.session_state.page = "map"
        st.rerun()
with nav2:
    st.caption("Your choices matter: inspect the data, make a call, and see what your decision reveals.")

if st.session_state.page == "map":
    st.markdown("## 🗺️ Investigation map")
    st.write("Solve each case to unlock the next one. Complete all five to earn the **Master Detective** badge.")
    cols = st.columns(5)
    for i, (num, title, emoji, subtitle, concept) in enumerate(LEVELS):
        level = i + 1
        done = str(level) in st.session_state.completed
        unlocked = level <= st.session_state.unlocked
        with cols[i]:
            status = "✅ SOLVED" if done else ("🔓 OPEN" if unlocked else "🔒 LOCKED")
            st.markdown(f'<div class="level-card {"done" if done else ("active" if unlocked else "")}"><div style="font-size:2rem">{emoji}</div><b>CASE {num}</b><br><b>{title}</b><br><span class="small-muted">{concept}</span><br><br><b>{status}</b></div>', unsafe_allow_html=True)
            if unlocked:
                if st.button("Play again" if done else "Investigate", key=f"open_{level}", use_container_width=True):
                    st.session_state.page = f"level{level}"
                    st.rerun()
            else:
                st.button("Locked", key=f"locked_{level}", disabled=True, use_container_width=True)
    if len(st.session_state.completed) == 5:
        st.balloons()
        st.markdown('<div class="hero"><h1>🏆 Master Data Detective!</h1><p>You solved every mystery and learned to question the data, not just the story.</p></div>', unsafe_allow_html=True)
    st.stop()

# ----------------------------- LEVEL 1 --------------------------------
if st.session_state.page == "level1":
    level_header(1)
    st.write("A weather station recorded temperatures for one week. Some readings are missing. Your job is to fill the gaps sensibly.")
    df = pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],"Temperature (°C)":[28,29,np.nan,30,31,np.nan,29]})
    st.dataframe(df, use_container_width=True, hide_index=True)
    median = df["Temperature (°C)"].median()
    mean = df["Temperature (°C)"].mean()
    st.markdown("### 🔎 Your evidence")
    st.write(f"Known readings: **{df['Temperature (°C)'].count()}** · Average of known readings: **{mean:.1f}°C** · Middle value (median): **{median:.1f}°C**")
    choice = st.radio("Which value would be a sensible way to fill the missing temperatures in this small, fairly consistent dataset?", ["Replace them with 0°C", "Replace them with the median (29°C)", "Delete the entire week", "Guess a different value for every missing day"], key="l1_choice")
    with st.expander("💡 Need a hint?"):
        st.write("A missing reading is not the same as zero. A typical value from the available readings can be a reasonable replacement.")
        if st.button("Use hint — this reduces XP", key="hint1"):
            if "1" not in st.session_state.hints_used: st.session_state.hints_used.append("1")
    if st.button("Submit investigation", key="submit1"):
        correct = choice.startswith("Replace them with the median")
        finish_case(1, correct, f"The median is {median:.1f}°C. Replacing missing values with a representative value is one form of data cleaning. Always consider why values are missing before choosing a method.")
    if "1" in st.session_state.completed and st.button("➡️ Back to case map", key="back1"):
        st.session_state.page = "map"; st.rerun()

# ----------------------------- LEVEL 2 --------------------------------
elif st.session_state.page == "level2":
    level_header(2)
    st.write("A courier company recorded delivery times. One delivery may be suspiciously slow. Find the unusual record.")
    times = [31,34,29,33,35,30,32,34,31,33,95,29,32]
    df = pd.DataFrame({"Parcel ID":[f"P-{i+101}" for i in range(len(times))],"Delivery time (minutes)":times})
    st.dataframe(df, use_container_width=True, hide_index=True)
    q1, q3 = np.percentile(times, [25,75])
    iqr = q3-q1
    upper = q3 + 1.5*iqr
    outliers = [x for x in times if x > upper or x < q1-1.5*iqr]
    fig = px.box(df, y="Delivery time (minutes)", points="all", title="Delivery-time distribution")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", title_font_size=18)
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"Using the IQR rule: Q1 = **{q1:.1f}**, Q3 = **{q3:.1f}**, IQR = **{iqr:.1f}**. Values above **{upper:.1f} minutes** are flagged.")
    choice = st.radio("Which delivery time should be investigated as an outlier?", ["29 minutes", "34 minutes", "95 minutes", "All deliveries are equally typical"], key="l2_choice")
    with st.expander("💡 Need a hint?"):
        st.write("Look for a value far away from the main cluster of delivery times.")
        if st.button("Use hint — this reduces XP", key="hint2"):
            if "2" not in st.session_state.hints_used: st.session_state.hints_used.append("2")
    if st.button("Submit investigation", key="submit2"):
        correct = choice == "95 minutes"
        finish_case(2, correct, f"The IQR method flags values outside Q1 − 1.5×IQR and Q3 + 1.5×IQR. Here, {outliers} is an outlier. An outlier is unusual, but it is not automatically an error.")
    if "2" in st.session_state.completed and st.button("➡️ Back to case map", key="back2"):
        st.session_state.page = "map"; st.rerun()

# ----------------------------- LEVEL 3 --------------------------------
elif st.session_state.page == "level3":
    level_header(3)
    st.write("A teacher wonders whether students who study longer tend to score higher. Explore the paired data and find the relationship.")
    df = pd.DataFrame({"Study hours":[1,2,2.5,3,4,4.5,5,6,7,8],"Exam score":[42,48,51,55,63,66,70,78,84,91]})
    corr = df["Study hours"].corr(df["Exam score"])
    fig = px.scatter(df, x="Study hours", y="Exam score", trendline="ols", title="Study hours vs exam score", labels={"Study hours":"Hours studied","Exam score":"Exam score (%)"})
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.write(f"Calculated correlation coefficient: **{corr:.2f}** (closer to +1 means a stronger positive linear relationship).")
    choice = st.radio("What pattern does this dataset show?", ["Positive correlation: more study hours tend to go with higher scores", "Negative correlation: more study hours tend to go with lower scores", "No relationship at all"], key="l3_choice")
    with st.expander("💡 Need a hint?"):
        st.write("Look at the direction of the points as you move from left to right.")
        if st.button("Use hint — this reduces XP", key="hint3"):
            if "3" not in st.session_state.hints_used: st.session_state.hints_used.append("3")
    if st.button("Submit investigation", key="submit3"):
        correct = choice.startswith("Positive correlation")
        finish_case(3, correct, f"The correlation is {corr:.2f}, showing a strong positive relationship in this dataset. Correlation describes how variables move together; it does not, by itself, prove that one causes the other.")
    if "3" in st.session_state.completed and st.button("➡️ Back to case map", key="back3"):
        st.session_state.page = "map"; st.rerun()

# ----------------------------- LEVEL 4 --------------------------------
elif st.session_state.page == "level4":
    level_header(4)
    st.write("A college has 100 students: 70 are from engineering and 30 are from arts. A survey asks about campus food. The survey team only asks students in the engineering lab.")
    population = pd.DataFrame({"Group":["Engineering","Arts"],"Students":[70,30],"Share (%)":[70,30]})
    sample = pd.DataFrame({"Group":["Engineering","Arts"],"Survey responses":[20,0],"Share of sample (%)":[100,0]})
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Whole college (population)**")
        st.dataframe(population, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**Survey sample**")
        st.dataframe(sample, use_container_width=True, hide_index=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Population", x=["Engineering","Arts"], y=[70,30]))
    fig.add_trace(go.Bar(name="Survey sample", x=["Engineering","Arts"], y=[100,0]))
    fig.update_layout(barmode="group", title="Who is represented?", yaxis_title="Share (%)", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    choice = st.radio("Can this survey fairly represent the opinions of the whole college?", ["Yes, 20 responses are always enough", "No, it excludes arts students and over-represents engineering", "Yes, because engineering students are the majority"], key="l4_choice")
    with st.expander("💡 Need a hint?"):
        st.write("A sample should give relevant groups a fair chance to be represented. Who has zero responses?")
        if st.button("Use hint — this reduces XP", key="hint4"):
            if "4" not in st.session_state.hints_used: st.session_state.hints_used.append("4")
    if st.button("Submit investigation", key="submit4"):
        correct = choice.startswith("No, it excludes")
        finish_case(4, correct, "This is sampling bias: the method systematically leaves out arts students. A larger sample would not automatically fix the problem if it is still selected in the same biased way.")
    if "4" in st.session_state.completed and st.button("➡️ Back to case map", key="back4"):
        st.session_state.page = "map"; st.rerun()

# ----------------------------- LEVEL 5 --------------------------------
elif st.session_state.page == "level5":
    level_header(5)
    st.write("A town notices that ice-cream sales and swimming incidents both rise during summer. A headline claims: “Eating ice cream causes swimming incidents!” Is the headline justified?")
    df = pd.DataFrame({"Temperature (°C)":[20,22,24,26,28,30,32,34],"Ice cream sales":[12,15,18,22,27,31,36,40],"Swimming incidents":[1,2,2,4,5,7,8,10]})
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**The evidence**")
        st.dataframe(df, use_container_width=True, hide_index=True)
    with c2:
        fig = px.scatter(df, x="Ice cream sales", y="Swimming incidents", trendline="ols", title="Ice-cream sales vs swimming incidents")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### 🧠 Final deduction")
    choice = st.radio("Which explanation is most scientifically careful?", ["Ice cream causes swimming incidents because both rise together", "They are correlated, but warmer weather may increase both; this does not prove causation", "There is no relationship because the variables are different"], key="l5_choice")
    with st.expander("💡 Need a hint?"):
        st.write("Think about a third factor that changes in summer and could affect both variables.")
        if st.button("Use hint — this reduces XP", key="hint5"):
            if "5" not in st.session_state.hints_used: st.session_state.hints_used.append("5")
    if st.button("Submit final deduction", key="submit5"):
        correct = choice.startswith("They are correlated")
        finish_case(5, correct, "The hidden variable is temperature (or season). Hot weather can increase ice-cream sales and swimming activity. The two variables may be correlated, but that does not establish that one causes the other.")
    if "5" in st.session_state.completed and st.button("🏆 Return to case map", key="back5"):
        st.session_state.page = "map"; st.rerun()

# ----------------------------- FOOTER --------------------------------
st.markdown("---")
st.caption("DATA DETECTIVE • Learn by investigating • Built with Python, Streamlit, Pandas, NumPy and Plotly")
with st.expander("⚙️ Game controls"):
    if st.button("Restart game (reset all progress)", type="secondary"):
        for key in ["character","unlocked","completed","xp","answers","hints_used","page"]:
            if key in st.session_state: del st.session_state[key]
        st.rerun()
