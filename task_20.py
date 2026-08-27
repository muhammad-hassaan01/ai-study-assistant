import streamlit as st

import requests

from google import genai

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered"
)

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("📚 AI Study Assistant")
st.subheader("Your personal AI tutor for school subjects")
st.write("Ask me any school question.")

st.divider()

DATABASE_URL = "https://ai-study-assistant-e9edd-default-rtdb.firebaseio.com/"



if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "edit_profile" not in st.session_state:
    st.session_state.edit_profile = False


if not st.session_state.logged_in:

    st.sidebar.title("👤 Welcome!")

    account_type = st.sidebar.radio(
        "Choose an option",
        ["Login", "Create Account"]
    )

    username = st.sidebar.text_input(
        "Username"
    ).lower().strip()

    if account_type == "Login":

        if st.sidebar.button("Login"):

            if username:

                user_response = requests.get(
                    DATABASE_URL + f"/users/{username}.json"
                )

                if user_response.json():

                    user_data = user_response.json()

                    st.session_state.username = username
                    st.session_state.user_name = user_data.get("name", "")
                    st.session_state.age = user_data.get("age", 0)
                    st.session_state.favorite_subject = user_data.get("favorite_subject", "")
                    st.session_state.learning_goal = user_data.get("learning_goal", "")
                    st.session_state.usage_count = user_data.get("usage_count", 0)

                    st.session_state.logged_in = True

                    st.rerun()

                else:

                    st.sidebar.error(
                        "Username not found. Please create an account."
                    )

    else:

        st.sidebar.info(
            "Create a username and profile."
        )

        if st.sidebar.button("Create Account"):

            if username:

                user_response = requests.get(
                    DATABASE_URL + f"/users/{username}.json"
                )

                if user_response.json():

                    st.sidebar.error(
                        "Username already exists. Choose another one."
                    )

                else:

                    st.session_state.username = username
                    st.session_state.user_name = ""
                    st.session_state.age = 15
                    st.session_state.favorite_subject = "Math"
                    st.session_state.learning_goal = "Exam Prep"
                    st.session_state.logged_in = True
                    st.session_state.edit_profile = True

                    requests.put(
                        DATABASE_URL + f"/users/{username}.json",
                        json={
                            "name": "",
                            "age": 15,
                            "favorite_subject": "Math",
                            "learning_goal": "Exam Prep",
                            "usage_count": 0,
                            "messages": []
                        }
                    )

                    st.rerun()



if st.session_state.logged_in:

    if st.session_state.user_name == "" or st.session_state.edit_profile:

        st.sidebar.title("👤 Your Profile")

        name = st.sidebar.text_input(
            "Your name",
            value=st.session_state.user_name
        )

        age = st.sidebar.number_input(
            "Your age",
            min_value=5,
            max_value=100,
            value=st.session_state.age
        )

        favorite_subject = st.sidebar.selectbox(
            "Favorite subject",
            [
                "Math",
                "Science",
                "English",
                "Computer Science",
                "Physics",
                "Chemistry",
                "Biology",
                "History"
            ]
        )

        learning_goal = st.sidebar.selectbox(
            "Learning goal",
            [
                "Exam Prep",
                "General Knowledge",
                "Skill Building"
            ]
        )

        if st.sidebar.button("Save Profile"):

            if name:

                st.session_state.user_name = name
                st.session_state.age = age
                st.session_state.favorite_subject = favorite_subject
                st.session_state.learning_goal = learning_goal
                st.session_state.edit_profile = False

                requests.put(
                    DATABASE_URL + f"/users/{st.session_state.username}.json",
                    json={
                        "name": name,
                        "age": age,
                        "favorite_subject": favorite_subject,
                        "learning_goal": learning_goal,
                        "usage_count": st.session_state.usage_count,
                        "messages": []
                    }
                )

                st.rerun()

    else:

        st.sidebar.success(
            f"👋 Welcome back, {st.session_state.user_name}!"
        )

        st.sidebar.write(
            f"Times used: {st.session_state.usage_count}"
        )

        if st.sidebar.button("✏️ Update Profile"):

            st.session_state.edit_profile = True
            st.rerun()


subject = st.sidebar.selectbox(
    "Choose a Subject",
    ["Math", "Science", "English", "Computer Science", "Physics", "Chemistry", "Biology", "History"]
)

if st.session_state.logged_in and st.session_state.user_name:

    subject = st.sidebar.selectbox(
        "Choose a Subject",
        [
            "Math",
            "Science",
            "English",
            "Computer Science",
            "Physics",
            "Chemistry",
            "Biology",
            "History"
        ]
    )

    difficulty = st.sidebar.selectbox(
        "Choose Difficulty Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    st.sidebar.divider()

    st.sidebar.subheader("⚙️ Settings")

    response_style = st.sidebar.selectbox(
        "Response Style",
        [
            "Simple and Clear",
            "Detailed Explanation",
            "Step-by-Step",
            "Short Answer"
        ]
    )

    st.sidebar.write(
        "Customize how the AI explains your answers."
    )

response = requests.get(
    DATABASE_URL + f"/users/{st.session_state.username}/messages.json"
)

if response.json():
    st.session_state.messages = response.json()
else:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
  
           
if st.session_state.logged_in and st.session_state.user_name:

    question = st.chat_input("Ask your question...")

else:

    question = None
    st.info("👤 Please create an account and enter your name before asking a question.")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    prompt = f"""
    You are an AI Study Assistant.

    Subject: {subject}
    Difficulty Level: {difficulty}
    Response Style: {response_style}

    Answer the student's question according to the selected
    subject and difficulty level.

If the subject is Math:
Focus on formulas, calculations, and step-by-step solutions.

If the subject is Science:
Focus on scientific concepts and simple explanations.

If the subject is English:
Focus on grammar, vocabulary, writing, and literature.

If the subject is Computer Science:
Explain programming, algorithms, computers, and technology clearly.

If the subject is Physics:
Focus on formulas, concepts, units, and calculations.

If the subject is Chemistry:
Focus on reactions, formulas, elements, and chemical concepts.

If the subject is Biology:
Focus on living organisms, cells, systems, and biological concepts.

If the subject is History:
Focus on historical events, people, dates, causes, and effects.

    Explain everything clearly for a school student.

    Student's question:
    {question}
    """

    recent_messages =  st.session_state.messages[-5:]

    for message in recent_messages:
        prompt += f"{message['role']} : {message['content']}"


    response = client.models.generate_content(
        model = "gemini-3-flash-preview",
        contents = prompt
    )

    answer = response.text

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
    
    with st.chat_message("assistant"):
        st.write(answer)

requests.put(
    DATABASE_URL + f"/users/{st.session_state.username}/messages.json",
    json=st.session_state.messages
)

st.divider()

st.caption(
    "📚 AI Study Assistant | Built with Python, "
    "Streamlit, Gemini API & Firebase"
)
