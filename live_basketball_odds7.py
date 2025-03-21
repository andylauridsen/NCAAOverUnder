import streamlit as st
import requests
import re

def parse_time_input(time_str):
    match = re.match(r"(\d+):(\d+)", time_str)
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return minutes + seconds / 60.0
    return 20.0  # default fallback

def calculate_live_over_under(score_a, score_b, time_left, team_a_fouls, team_b_fouls, bonus_a, bonus_b, timeouts_a, timeouts_b, seed_a, seed_b, round_num):
    current_total = score_a + score_b
    estimated_remaining_points = (current_total / (40 - time_left)) * time_left * 1.05

    foul_factor = 1.0
    if bonus_a and bonus_b:
        foul_factor += 0.08
    elif bonus_a or bonus_b:
        foul_factor += 0.04

    point_margin = abs(score_a - score_b)
    if time_left < 3:
        if point_margin <= 5:
            estimated_remaining_points += 8
        elif point_margin > 10:
            estimated_remaining_points -= 5
    if time_left <= 1:
        if point_margin >= 15:
            estimated_remaining_points = min(estimated_remaining_points, 4)
        if point_margin >= 20:
            estimated_remaining_points = min(estimated_remaining_points, 2)
        if time_left <= 0.5 and point_margin >= 15:
            estimated_remaining_points = min(estimated_remaining_points, 1)

    if timeouts_a + timeouts_b > 3:
        estimated_remaining_points *= 0.98

    seed_diff = abs(seed_a - seed_b)
    if seed_diff >= 7 and time_left < 10:
        estimated_remaining_points *= 0.90
    elif seed_diff <= 3 and time_left < 5:
        estimated_remaining_points += 5

    if round_num >= 4:
        estimated_remaining_points *= 0.92
    elif round_num == 1:
        estimated_remaining_points *= 1.05

    projected_total = current_total + estimated_remaining_points * foul_factor
    return round(projected_total, 1)

def calculate_halftime_score(score_a, score_b, time_left, team_a_fouls, team_b_fouls, bonus_a, bonus_b, timeouts_a, timeouts_b):
    current_total = score_a + score_b
    elapsed_time = 20 - time_left

    expected_half = 70  # Average first-half total
    progress = elapsed_time / 20
    expected_by_now = expected_half * progress
    delta = current_total - expected_by_now

    projected_total = expected_half + delta * 1.15
    return round(projected_total, 1)

st.title("Live NCAA Tournament Over/Under Predictor")

score_a = st.number_input("Team A Score", min_value=0, value=50)
score_b = st.number_input("Team B Score", min_value=0, value=50)
time_left_str = st.text_input("Time Left (mm:ss)", value="20:00")
time_left = parse_time_input(time_left_str)
team_a_fouls = st.number_input("Team A Fouls", min_value=0, value=5)
team_b_fouls = st.number_input("Team B Fouls", min_value=0, value=5)
bonus_a = st.checkbox("Team A in Bonus?")
bonus_b = st.checkbox("Team B in Bonus?")
timeouts_a = st.number_input("Team A Timeouts Left", min_value=0, max_value=5, value=3)
timeouts_b = st.number_input("Team B Timeouts Left", min_value=0, max_value=5, value=3)
seed_a = st.number_input("Team A Seed", min_value=1, max_value=16, value=1)
seed_b = st.number_input("Team B Seed", min_value=1, max_value=16, value=16)

round_num = st.selectbox("Select Tournament Round", [
    (1, "First Round"),
    (2, "Second Round"),
    (3, "Sweet 16"),
    (4, "Elite Eight"),
    (5, "Final Four"),
    (6, "Championship")
], format_func=lambda x: x[1])[0]

if st.button("Predict Final Score"):
    projected_total = calculate_live_over_under(score_a, score_b, time_left, team_a_fouls, team_b_fouls, bonus_a, bonus_b, timeouts_a, timeouts_b, seed_a, seed_b, round_num)
    st.write(f"### Full Game Projected Over/Under: {projected_total}")

if st.button("Predict Halftime Score"):
    projected_half = calculate_halftime_score(score_a, score_b, time_left, team_a_fouls, team_b_fouls, bonus_a, bonus_b, timeouts_a, timeouts_b)
    st.write(f"### Projected Halftime Score: {projected_half}")

st.markdown("---")
st.markdown("**Version 1.5 – Tweaked scoring pace, foul factor, and timeout impact to reduce under-prediction**")
