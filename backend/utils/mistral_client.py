import os
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Pre-defined concern responses (clinically accurate)
CONCERN_RESPONSES = {
    "increased_shedding": {
        "response": "This is completely normal and actually a POSITIVE sign. In the first 2-6 weeks, old, weak hair (telogen phase) falls out to make room for new, thicker hair (anagen phase). This process is called 'telogen effluvium' and it means the treatment is working. The shedding typically lasts 2-4 weeks and then subsides. Continue your treatment consistently.",
        "escalate": False
    },
    "itchy_scalp": {
        "response": "Mild itching is a common side effect of Minoxidil, especially in the first few weeks. This usually subsides as your scalp adjusts. You can try: (1) Using a gentle, anti-itch shampoo, (2) Applying a light moisturizer to the scalp, (3) Ensuring the solution is fully dry before bed. If itching persists beyond 4 weeks or becomes severe, please consult a dermatologist.",
        "escalate": False
    },
    "flaking_dryness": {
        "response": "Flaking and dryness are common with topical Minoxidil solutions. This is often caused by the alcohol in the solution drying the scalp. Solutions: (1) Use a gentle moisturizing shampoo, (2) Apply a scalp moisturizer after the solution dries, (3) Stay hydrated. If flaking is accompanied by redness or severe irritation, consult a doctor.",
        "escalate": False
    },
    "redness_irritation": {
        "response": "Some redness or mild irritation can occur, especially in the first 2 weeks. However, if redness is persistent, spreading, or accompanied by burning/swelling, this may indicate contact dermatitis. Suggestions: (1) Reduce application to once daily temporarily, (2) Ensure scalp is clean and dry before application, (3) If symptoms persist beyond 2 weeks, please consult a dermatologist.",
        "escalate": True  # Potentially needs doctor attention
    },
    "missed_dose": {
        "response": "Don't worry! Missing a single dose does not undo your progress. Consistency is important, but occasional misses are normal. Simply resume your regular schedule with your next dose. Do NOT apply extra to 'make up' for the missed dose. Tip: Set a daily alarm to help remember your doses.",
        "escalate": False
    },
    "no_visible_results": {
        "response": "Hair growth is a slow biological process. Visible results typically appear after 3-6 months of consistent use. In the meantime, trust the process: (1) You're in the early stages where foundation work is happening beneath the surface, (2) The shedding phase is actually proof the treatment is active, (3) Take monthly photos to track subtle changes. Stay patient and consistent!",
        "escalate": False
    },
    "scalp_tightness": {
        "response": "A sensation of scalp tightness can occur due to the solution drying on the scalp. This is usually harmless. Solutions: (1) Gently massage your scalp for 1-2 minutes after application, (2) Ensure you're not using too much product (1ml is sufficient), (3) Apply a light scalp moisturizer after the solution dries completely. If tightness is painful or persistent, consult a doctor.",
        "escalate": False
    }
}

def get_mistral_client():
    """Create and return a Mistral AI client"""
    if not MISTRAL_API_KEY:
        raise ValueError("Mistral API key must be set in environment variables")
    return Mistral(api_key=MISTRAL_API_KEY)

def _generate_contextual_fallback(concern_type: str, user_context: dict = None) -> dict:
    """Intelligent clinical fallback tailored to hair regrowth treatments and app questions."""
    c_lower = concern_type.lower()
    
    if any(q in c_lower for q in ["how can you help", "what can you do", "help me", "who are you", "what is this"]):
        return {
            "response": (
                "👋 **I am your Regrowth OS Clinical & Habit Companion!**\n\n"
                "I am here to guide you through your hair regrowth journey (Minoxidil + Finasteride):\n\n"
                "• **Normalizing the Shedding Phase (Weeks 2–6):** Reminding you why temporary shedding is positive proof old dormant follicles are resetting.\n"
                "• **Routine & Dose Tracking:** Helping you maintain your daily application streak and manage missed doses safely.\n"
                "• **Symptom & Side-Effect Guidance:** Answering questions on scalp itch, flaking, redness, and dryness.\n"
                "• **Photo & Progress Verification:** Encouraging standardized scalp tracking so you can see subtle regrowth month-to-month.\n\n"
                "Ask me about any scalp symptom, routine question, or timeline milestone anytime!"
            ),
            "escalate": False
        }
    
    if any(k in c_lower for k in ["shed", "losing hair", "fall", "shower", "hair fall"]):
        return {
            "response": (
                "🌱 **Increased shedding is normal and expected.**\n\n"
                "Between weeks 2 to 6 of Minoxidil/Finasteride treatment, a temporary shed (telogen effluvium) happens because follicles rapidly reset. "
                "Weak, miniaturized hairs are pushed out to allow thicker, healthier anagen hairs to grow in.\n\n"
                "• **Action:** Continue applying your dose consistently. Shedding usually subsides within 2–4 weeks.\n"
                "• **Note:** Do not stop your treatment, as stopping resets the follicle cycle."
            ),
            "escalate": False
        }

    if any(k in c_lower for k in ["miss", "forgot", "skip", "dose"]):
        return CONCERN_RESPONSES["missed_dose"]
    
    if any(k in c_lower for k in ["itch", "scratch"]):
        return CONCERN_RESPONSES["itchy_scalp"]
    
    if any(k in c_lower for k in ["flake", "dandruff", "dry"]):
        return CONCERN_RESPONSES["flaking_dryness"]
    
    if any(k in c_lower for k in ["result", "grow", "see", "change"]):
        return CONCERN_RESPONSES["no_visible_results"]
    
    if any(k in c_lower for k in ["red", "burn", "irritat", "pain"]):
        return CONCERN_RESPONSES["redness_irritation"]

    # General reassuring clinical guidance
    day_info = f" (Treatment started: {user_context.get('treatment_start_date')})" if user_context and user_context.get("treatment_start_date") else ""
    return {
        "response": (
            f"Here is clinical guidance regarding **{concern_type}**{day_info}:\n\n"
            "When using topical Minoxidil & Finasteride regimens, your scalp undergoes cellular adaptation over 90+ days. "
            "Mild sensations like slight tingling, mild dryness, or temporary shedding are common signs of follicle activity.\n\n"
            "• **Recommended Action:** Ensure your scalp is clean and completely dry before applying 1 ml. Massage gently and let it absorb for at least 4 hours.\n"
            "• **When to Consult:** If you experience severe redness, persistent dizziness, chest palpitations, or swelling, pause use and consult your doctor.\n\n"
            "*General educational information — not a substitute for personal medical advice.*"
        ),
        "escalate": False
    }

async def get_ai_response_for_concern(concern_type: str, user_context: dict = None) -> dict:
    """
    Get AI response for a specific concern.
    First checks predefined responses, then queries Mistral AI with a hair regrowth clinical prompt,
    falling back to specialized clinical guidance if rate-limited.
    """
    cleaned_key = concern_type.strip().lower().replace(" ", "_")
    if cleaned_key in CONCERN_RESPONSES:
        return CONCERN_RESPONSES[cleaned_key]
    
    if concern_type in CONCERN_RESPONSES:
        return CONCERN_RESPONSES[concern_type]
    
    # Query Mistral AI using working chat models (ministral-8b-latest, ministral-3b-latest)
    try:
        client = get_mistral_client()
        
        user_info_str = ""
        if user_context:
            user_info_str = f"User Name: {user_context.get('name')}, Treatment Start Date: {user_context.get('treatment_start_date')}, Dosage Frequency: {user_context.get('dosage_frequency')}x/day."
        
        system_prompt = (
            "You are the clinical & habit assistant in 'Regrowth OS' (a dedicated hair treatment tracking app for Man Matters). "
            "Your mission is to help users succeed through their 90-day Minoxidil + Finasteride journey by reducing anxiety around temporary shedding, "
            "encouraging daily dose compliance, explaining scalp symptoms (itching, flaking, tightness, shedding), and tracking progress. "
            "Tone: Empathetic, scientifically accurate, encouraging, structured with markdown bullet points. "
            "Keep responses concise (100–160 words). "
            "If asked 'How can you help me?' or general greetings, explain your exact role in their hair regrowth regimen."
        )

        user_prompt = f"User Question / Concern: \"{concern_type}\"\n{user_info_str}"

        # Try ministral-8b-latest first, then fallback to ministral-3b-latest
        response_text = None
        for model_name in ["ministral-8b-latest", "ministral-3b-latest"]:
            try:
                chat_res = client.chat.complete(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=300
                )
                if chat_res and chat_res.choices:
                    response_text = chat_res.choices[0].message.content
                    break
            except Exception as model_err:
                print(f"Mistral model {model_name} error: {model_err}")
                continue
        
        if response_text:
            lowered = response_text.lower()
            needs_doctor = ("emergency" in lowered or "severe allergic" in lowered or "chest pain" in lowered)
            return {
                "response": response_text,
                "escalate": needs_doctor
            }
    except Exception as e:
        print(f"Mistral client error: {e}")

    # Fallback to rich clinical domain responses
    return _generate_contextual_fallback(concern_type, user_context)

def calculate_timeline_phase(day_number: int) -> dict:
    """
    Calculate the current treatment phase based on day number.
    """
    if day_number <= 14:
        return {
            "phase_name": "Adaptation Phase",
            "phase_message": "Your scalp is getting used to the treatment. Stay consistent — this is the foundation period.",
            "progress_percentage": (day_number / 90) * 100
        }
    elif day_number <= 45:
        return {
            "phase_name": "Shedding Peak",
            "phase_message": "Telogen reset in progress. Shedding now is proof the treatment is working. Old hair is making way for thicker, stronger hair.",
            "progress_percentage": (day_number / 90) * 100
        }
    elif day_number <= 90:
        return {
            "phase_name": "Early Vellus Growth",
            "phase_message": "Fine baby hairs are emerging. This is the early sign of regrowth. Keep going!",
            "progress_percentage": (day_number / 90) * 100
        }
    else:
        return {
            "phase_name": "Terminal Densification",
            "phase_message": "Your hair is thickening. Continue maintenance to preserve your results.",
            "progress_percentage": 100
        }

def calculate_streak_badge(streak_days: int) -> str:
    """Get badge name based on streak days"""
    if streak_days >= 90:
        return "Regrowth Champion"
    elif streak_days >= 60:
        return "Shedding Survivor"
    elif streak_days >= 30:
        return "One Month Strong"
    elif streak_days >= 7:
        return "Consistency Starter"
    return None
