import os
import sys
from google import genai
from google.genai import types

# Load environment variables (defaults represent stable configurations)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", "0.7"))
GEMINI_THINKING_BUDGET = int(os.environ.get("GEMINI_THINKING_BUDGET", "0"))
GEMINI_API_TIMEOUT_SECONDS = float(os.environ.get("GEMINI_API_TIMEOUT_SECONDS", "30"))
GEMINI_MAX_OUTPUT_TOKENS = int(os.environ.get("GEMINI_MAX_OUTPUT_TOKENS", "300"))

def get_client():
    if not GEMINI_API_KEY:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")
    return genai.Client(api_key=GEMINI_API_KEY)

def generate_npc_reply(system_instruction, chat_history, user_message):
    """
    Generates an NPC reply using the official google-genai SDK.
    
    Args:
        system_instruction (str): The concatenated rules, identity, and whitelist scenario facts.
        chat_history (list): A list of dicts representing past messages, structured as:
                             [{'sender_id': 'diao-wu-er', 'content': '...'}, ...]
        user_message (str): The latest message string sent by the user.
        
    Returns:
        str: The AI model's response.
    """
    client = get_client()
    
    # Map messages to types.Content structure matching SDK expectations.
    # Roles in Gemini are 'user' and 'model'.
    contents = []
    for msg in chat_history:
        role = "model" if msg['sender_id'] == 'zhang-meng' else "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg['content'])]
            )
        )
    
    # Append the final incoming message from the player
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        )
    )
    
    # Build content configuration dictionary
    config_params = {
        "temperature": GEMINI_TEMPERATURE,
        "max_output_tokens": GEMINI_MAX_OUTPUT_TOKENS,
        "system_instruction": system_instruction
    }
    
    # Only configure thinking budget if explicitly requested and greater than 0
    if GEMINI_THINKING_BUDGET > 0:
        config_params["thinking_config"] = types.ThinkingConfig(
            thinking_budget=GEMINI_THINKING_BUDGET
        )
        
    config = types.GenerateContentConfig(**config_params)
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config
        )
        if response and response.text:
            return response.text.strip()
        raise ValueError("Gemini returned an empty response. It might have been blocked by safety settings.")
    except Exception as e:
        print(f"❌ Gemini API execution error: {e}", file=sys.stderr)
        raise e
