import streamlit as st
import av
import cv2
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes

from drowsy_detection import VideoFrameHandler
from audio_handling import AudioFrameHandler


# ------------------ PAGE SETUP ------------------
st.set_page_config(
    page_title="D3 – Drowsiness Detection Dashboard",
    page_icon="😴",
    layout="wide"
)

# ------------------ CSS (NO SCROLL + FIXED LAYOUT) ------------------
st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            overflow: hidden !important;
        }

        .main { background-color: #0e1117 !important; }
        .stApp { background-color: #0e1117 !important; }

        h1, h2, h3, h4, h5, h6, p {
            color: #ffffff !important;
        }

        .title-main {
            text-align: center;
            font-size: 46px;
            font-weight: 800;
            color: #00c3ff;
            margin-bottom: -8px;
            text-shadow: 0px 0px 10px #0094c7;
        }

        .title-sub {
            text-align: center;
            font-size: 18px;
            color: #e0e0e0;
        }

        .instructions {
            background: #1c1f26;
            padding: 15px;
            border-left: 5px solid #00c3ff;
            border-radius: 10px;
            color: #dcdcdc;
            font-size: 14px;
        }

        video {
            height: 430px !important;
            width: 100% !important;
            object-fit: cover !important;
            border-radius: 10px;
        }

        .footer {
            text-align: center;
            margin-top: 10px;
            padding: 5px;
            color: #bdbdbd;
            font-size: 13px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------ TITLE ------------------
st.markdown("<div class='title-main'>D3</div>", unsafe_allow_html=True)
st.markdown("<div class='title-sub'>(Drowsiness Detection Dashboard)</div>", unsafe_allow_html=True)


# ------------------ SIDEBAR SETTINGS ------------------
with st.sidebar:

    st.markdown("## 🔧 Mode Selection")
    MODE = st.radio("Choose Mode:", ["🚗 Driving Mode", "💻 Work/Study Mode"])

    st.markdown("## ⚙️ Detection Settings")
    WAIT_TIME = st.slider("⏱ Alarm Delay (seconds)", 0.0, 5.0, 1.0, 0.25)
    EAR_THRESH = st.slider("👁 EAR Threshold", 0.0, 0.4, 0.18, 0.01)

    st.markdown("---")
    st.markdown("## ☕ Quick Break Spots")

    if MODE == "🚗 Driving Mode":
        st.markdown("Nearest Tea Points:")
        if st.button("🔎 Show Tea Points Nearby"):
            st.markdown(
                "[Click here to open in Maps](https://www.google.com/maps/search/tea+stall+near+me/)"
            )
    else:
        st.markdown("Nearest Coffee Shops:")
        if st.button("🔎 Show Coffee Shops Nearby"):
            st.markdown(
                "[Click here to open in Maps](https://www.google.com/maps/search/coffee+shop+near+me/)"
            )

thresholds = {"EAR_THRESH": EAR_THRESH, "WAIT_TIME": WAIT_TIME}


# ------------------ HANDLERS ------------------
video_handler = VideoFrameHandler()
audio_handler = AudioFrameHandler("audio/wake_up.wav")


# ------------------ CALLBACKS ------------------
def video_frame_callback(frame: av.VideoFrame):
    frm = frame.to_ndarray(format="bgr24")
    processed, alarm_state = video_handler.process(frm, thresholds)

    return av.VideoFrame.from_ndarray(processed, format="bgr24")


def audio_frame_callback(frame: av.AudioFrame):
    play = video_handler.play_alarm
    return audio_handler.process(frame, play_sound=play)


# ------------------ LAYOUT ------------------
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 🎥 Live Monitoring Feed")
    ctx = webrtc_streamer(
        key="d3-system",
        video_frame_callback=video_frame_callback,
        audio_frame_callback=audio_frame_callback,
        media_stream_constraints={"video": True, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_html_attrs=VideoHTMLAttributes(autoPlay=True, muted=False, controls=False)
    )

with col2:
    st.markdown("### 📘 Instructions")
    st.markdown(
        f"""
        <div class="instructions">
        <b>Active Mode:</b> {MODE}<br><br>

        <b>How It Works:</b><br>
        • System tracks your eye aspect ratio in real-time.<br>
        • When eyes stay closed beyond selected time → alarm triggers.<br><br>

        <b>Driving Mode:</b><br>
        • Safety alert appears: <i>"Take a break and pull your car aside"</i>.<br>
        • Button available to find nearest tea stalls.<br><br>

        <b>Work/Study Mode:</b><br>
        • Alert: <i>"Time for a coffee break"</i>.<br>
        • Button to find nearest coffee shops.<br><br>

        <b>Tips:</b><br>
        • Adjust EAR threshold for accuracy.<br>
        • Ensure good lighting.<br>
        • Keep your face clearly visible to the camera.<br>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------ FOOTER ------------------
st.markdown(
    """
    <div class='footer'>
        Developed by <b>Yajat Agarwal</b> | Enrollment No: <b>23102031</b>
    </div>
    """,
    unsafe_allow_html=True
)
