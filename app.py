import streamlit as st
import json
import anthropic
import openai

# Set up the Streamlit page
st.set_page_config(
    page_title="AI Prompt Debugger",
    page_icon="🔍",
    layout="wide"
)

# Apply Custom CSS for UI enhancements
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stButton button { width: 100%; background-color: #FF4B4B; color: white; border-radius: 5px; }
    .stButton button:hover { background-color: #FF2B2B; }
    .stTextArea textarea, .stTextInput input { border-radius: 5px; border: 1px solid #ddd; }
    .stTextArea textarea:focus, .stTextInput input:focus { border-color: #FF4B4B; box-shadow: 0 0 0 1px #FF4B4B; }
    h1 { color: #FF4B4B; font-size: 2.5rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

class PromptDebugger:
    def __init__(self):
        try:
            self.anthropic_client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            openai.api_key = st.secrets["OPENAI_API_KEY"]
        except KeyError:
            st.error("Missing API keys in Streamlit secrets.")
        
        self.model_providers = {
            "Anthropic": {
                "claude-3-opus-20240229": "Claude 3 Opus",
                "claude-3-sonnet-20240229": "Claude 3 Sonnet",
                "claude-3-haiku-20240307": "Claude 3 Haiku"
            },
            "OpenAI": {
                "gpt-4o": "GPT-4o",
                "gpt-4": "GPT-4",
                "gpt-3.5-turbo": "GPT-3.5 Turbo"
            }
        }

    def analyze_prompt(self, inputs):
        analysis_prompt = f"""
You are an AI expert specializing in debugging and analyzing conversational agent prompts.

Given the following inputs:

- **Bot Type**: {inputs['bot_type']}
- **System Prompt**: {inputs['system_prompt']}
- **Conversation History**: {json.dumps(inputs['conversation_history'], indent=2)}
- **Defective User Message**: {inputs['defective_user_message']}
- **Defective Agent Response**: {inputs['defective_agent_response']}
- **Issue Description**: {inputs['defective_description']}
- **Agent's Interpretation**: {inputs['agent_interpretation']}
- **Expected Behavior**: {inputs['expected_behavior']}
- **Behavioral Guidelines**: {inputs['behavioral_guidelines']}

### Tasks:
1. **Error Source Analysis**: Identify if the issue originates from the system prompt, guidelines, or model behavior.
2. **Suggestions for Improvements**: Provide modifications to enhance the system prompt and guidelines.
3. **Agent Interpretation Shift**: Explain how the agent's reasoning may change with the new modifications.

Output should be in JSON format:
{{
    "error_analysis": {{ "system_prompt": "...", "guidelines": "..." }},
    "suggestions": {{ "system_prompt": "...", "guidelines": "..." }},
    "interpretation_change": "..."
}}
        """

        try:
            if inputs['provider'] == "Anthropic":
                response = self.anthropic_client.messages.create(
                    model=inputs['model'],
                    max_tokens=4000,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                result = json.loads(response.content[0].text)
            else:
                response = openai.ChatCompletion.create(
                    model=inputs['model'],
                    messages=[
                        {"role": "system", "content": "You are an expert AI debugger."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.2
                )
                result = json.loads(response.choices[0].message.content)

            return result
        except Exception as e:
            st.error(f"Analysis Error: {e}")
            return {}

def main():
    st.title("🔍 AI Prompt Debugger")
    debugger = PromptDebugger()

    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("Configuration")
        bot_type = st.selectbox("🤖 Bot Type", ["Text Bot", "Voice Bot"])
        provider = st.selectbox("🏢 Model Provider", list(debugger.model_providers.keys()))
        model = st.selectbox("🧠 Model", list(debugger.model_providers[provider].keys()),
                             format_func=lambda x: debugger.model_providers[provider][x])
    
    with col2:
        st.subheader("System & Guidelines")
        system_prompt = st.text_area("System Prompt", height=150)
        behavioral_guidelines = st.text_area("Behavioral Guidelines", height=150)

        st.subheader("Conversation History")
        num_exchanges = st.number_input("Number of Exchanges", min_value=1, value=1)
        conversation_history = []
        for i in range(num_exchanges):
            st.markdown(f"**Exchange {i+1}**")
            user_msg = st.text_area(f"User Message {i+1}")
            agent_msg = st.text_area(f"Agent Response {i+1}")
            if user_msg:
                conversation_history.append({"role": "user", "content": user_msg})
            if agent_msg:
                conversation_history.append({"role": "assistant", "content": agent_msg})
        
        st.subheader("Defective Interaction")
        defective_user_message = st.text_area("User Message")
        defective_agent_response = st.text_area("Agent Response")
        defective_description = st.text_area("Issue Description")
        agent_interpretation = st.text_area("Agent Interpretation")
        expected_behavior = st.text_area("Expected Behavior")
    
    if st.button("🔍 Analyze Prompt"):
        if not all([system_prompt, defective_user_message, defective_agent_response, defective_description, agent_interpretation, expected_behavior, behavioral_guidelines]):
            st.warning("⚠️ Please fill in all required fields.")
        else:
            with st.spinner("🔄 Analyzing..."):
                inputs = {
                    "bot_type": bot_type,
                    "system_prompt": system_prompt,
                    "conversation_history": conversation_history,
                    "defective_user_message": defective_user_message,
                    "defective_agent_response": defective_agent_response,
                    "defective_description": defective_description,
                    "agent_interpretation": agent_interpretation,
                    "expected_behavior": expected_behavior,
                    "behavioral_guidelines": behavioral_guidelines,
                    "provider": provider,
                    "model": model
                }
                analysis = debugger.analyze_prompt(inputs)
                st.json(analysis)

if __name__ == "__main__":
    main()
