import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Soundscape: Przyjemność-Wydarzeniowość", layout="wide")

st.title("Ocena soundscape: Przyjemność-Wydarzeniowość")
st.caption(
    "Skala ocen 0–100. Wykres aktualizuje się na żywo. "
    "Współrzędne liczone metodą ISO 12913-3:2025 z normalizacją (Mitchell, 2025)."
)

# --- KONFIGURACJA SKALI ---
MIN_SCORE = 0
MAX_SCORE = 100
DEFAULT_SCORE = 50
mu = (MIN_SCORE + MAX_SCORE) / 2.0
rho = (MAX_SCORE - MIN_SCORE) / 2.0

# --- ATRYBUTY I KĄTY ---
ATTRS = [
    ("Przyjemne", 0),
    ("Tętniące życiem", 69),
    ("Bogate w wydarzenia", 91),
    ("Chaotyczne", 128),
    ("Dokuczliwe", 176),
    ("Monotonne", 266),
    ("Ubogie w wydarzenia", 274),
    ("Spokojne", 339),
]

angles_deg = np.array([deg for _, deg in ATTRS], dtype=float)
angles_rad = np.deg2rad(angles_deg)
cos_t = np.cos(angles_rad)
sin_t = np.sin(angles_rad)

def compute_pe(scores: np.ndarray):
    centered = scores - mu
    p_raw = np.sum(cos_t * centered)
    e_raw = np.sum(sin_t * centered)
    p_max = rho * np.sum(np.abs(cos_t))
    e_max = rho * np.sum(np.abs(sin_t))
    p = p_raw / p_max if p_max > 0 else 0.0
    e = e_raw / e_max if e_max > 0 else 0.0
    return float(np.clip(p, -1, 1)), float(np.clip(e, -1, 1))

# --- INICJALIZACJA ---
if "scores" not in st.session_state:
    st.session_state.scores = [DEFAULT_SCORE] * len(ATTRS)
for i in range(len(ATTRS)):
    if f"slider_{i}" not in st.session_state:
        st.session_state[f"slider_{i}"] = DEFAULT_SCORE
    if f"num_{i}" not in st.session_state:
        st.session_state[f"num_{i}"] = DEFAULT_SCORE

# --- CALLBACKI ---
def sync_from_slider(i):
    value = int(st.session_state[f"slider_{i}"])
    st.session_state[f"num_{i}"] = value
    st.session_state.scores[i] = value

def sync_from_number(i):
    value = int(st.session_state[f"num_{i}"])
    st.session_state[f"slider_{i}"] = value
    st.session_state.scores[i] = value

def reset_one(i):
    st.session_state[f"slider_{i}"] = DEFAULT_SCORE
    st.session_state[f"num_{i}"] = DEFAULT_SCORE
    st.session_state.scores[i] = DEFAULT_SCORE

def reset_all():
    for i in range(len(ATTRS)):
        st.session_state[f"slider_{i}"] = DEFAULT_SCORE
        st.session_state[f"num_{i}"] = DEFAULT_SCORE
    st.session_state.scores = [DEFAULT_SCORE] * len(ATTRS)

# --- LAYOUT ---
left, right = st.columns([0.45, 0.55])

with left:
    st.subheader("Oceny atrybutów (0–100)")
    st.button("🔄 Resetuj wszystkie suwaki do 50", on_click=reset_all)

    for i, (name, _) in enumerate(ATTRS):
        cols = st.columns([0.6, 0.25, 0.15])
        key_slider = f"slider_{i}"
        key_num = f"num_{i}"

        with cols[0]:
            st.slider(
                name,
                MIN_SCORE,
                MAX_SCORE,
                int(st.session_state[key_slider]),
                step=1,
                key=key_slider,
                on_change=sync_from_slider,
                args=(i,),
            )
        with cols[1]:
            st.number_input(
                " ",
                MIN_SCORE,
                MAX_SCORE,
                int(st.session_state[key_num]),
                step=1,
                key=key_num,
                label_visibility="collapsed",
                on_change=sync_from_number,
                args=(i,),
            )
        with cols[2]:
            st.button("↺", key=f"reset_{i}", help="Resetuj do 50", on_click=reset_one, args=(i,))

    scores = np.array(st.session_state.scores, dtype=float)
    P, E = compute_pe(scores)
    st.markdown(f"**Przyjemność (P):** {P:+.3f}   **Wydarzeniowość (E):** {E:+.3f}")

with right:
    st.subheader("Przyjemność-Wydarzeniowość")
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Przyjemność (P)")
    ax.set_ylabel("Wydarzeniowość (E)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.axhline(0, linewidth=1, color = "black")
    ax.axvline(0, linewidth=1, color = "black")
    #circle = plt.Circle((0, 0), 1, fill=False, linestyle=":", linewidth=1)
    #ax.add_artist(circle)
    ax.scatter([P], [E], s=50, color = "blue")
    ax.text(P, E, f" ({P:+.2f}, {E:+.2f})", va="center", fontsize=6)
    st.pyplot(fig, use_container_width=False)

# --- REFERENCJA ---
with st.expander("Pokaż pozycje atrybutów na modelu kołowym (referencja kierunków)"):
    fig2, ax2 = plt.subplots(figsize=(3, 3))
    ax2.set_xlim(-1, 1)
    ax2.set_ylim(-1, 1)
    ax2.set_aspect("equal", adjustable="box")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.axhline(0, linewidth=1)
    ax2.axvline(0, linewidth=1)
    circle2 = plt.Circle((0, 0), 1, fill=False, linestyle=":", linewidth=1)
    ax2.add_artist(circle2)
    for (name, deg), c, s in zip(ATTRS, cos_t, sin_t):
        ax2.arrow(0, 0, c * 0.9, s * 0.9, head_width=0.02, length_includes_head=True)
        ax2.text(c * 0.95, s * 0.95, name, ha="center", va="center", fontsize=4)
    ax2.set_title("Kierunki atrybutów", fontsize=9)
    st.pyplot(fig2, use_container_width=False)
