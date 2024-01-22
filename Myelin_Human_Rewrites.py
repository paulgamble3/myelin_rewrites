import streamlit as st
import glob
import json
import random
from firebase.firebase_utils import write_task_item


st.title("Myelin - Rewriting Rachel Turns")
st.subheader("Read the following conversation snippet and then rate and rewrite the final turn.")

user_name = st.text_input("Enter your name:")

# transcripts in json turn format
# sample turns
def sample_transcript():
    transcript_files = glob.glob("transcripts/*.json")
    transcript_file = random.choice(transcript_files)
    with open(transcript_file) as f:
        transcript = json.load(f)
    return transcript

def sample_turn_from_transcript(transcript):
    selected = False

    while not selected:
        turn = random.choice(transcript)
        if turn["speaker"] == "assistant" and len(turn["utterance"]) > 20:
            selected = True

    turn_ind = transcript.index(turn)

    return {
        "turn": turn,
        "turn_ind": turn_ind
    }

def get_recent_conv_str(transcript, turn_ind):
    recent_conv = transcript[max(0, turn_ind - 5):turn_ind+1]
    recent_conv_str = ""
    for turn in recent_conv:
        if turn["speaker"] == "assistant":
            recent_conv_str += "Nurse: " + turn["utterance"] + "\n\n"
        if turn["speaker"] == "user":
            recent_conv_str += "Patient: " + turn["utterance"] + "\n\n"
    return recent_conv_str

# display the last few turns with Nurse: Patient:
transcript = sample_transcript()
turn_info = sample_turn_from_transcript(transcript)
turn = turn_info["turn"]
turn_ind = turn_info["turn_ind"]
recent_conv_str = get_recent_conv_str(transcript, turn_ind)

with st.container(border=True):
    st.write(recent_conv_str)

# rating
# field for rewrite
with st.form(key='my_form', clear_on_submit=True):
    st.write("Rate the final turn above on a scale of 1-7 for overall quality, where 1 is 'very bad' and 7 is 'very good'")
    rating = st.slider(label='Rating', min_value=1, max_value=7, step=1)
    st.write("Also provide a rewrite of the final turn. You can rewrite the turn however you like, but try to make it more natural and fluent. You can also add or remove information if you think it would improve the turn")
    rewrite = st.text_area(label='Rewrite')
    submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        # save rating and rewrite to firebase
        write_task_item({
            "rating": rating,
            "rewrite": rewrite,
            "turn": turn,
            "turn_ind": turn_ind,
            "transcript": transcript,
            "user_name": user_name
        }, "myelin_human_rewrites")

