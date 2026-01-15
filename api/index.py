from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import random
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS so the frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FORTUNES = [
    "The moon waits; your patience turns tide into triumph.",
    "A quiet choice tonight becomes a loud win tomorrow.",
    "Your craft deepens when you finish what you begin.",
    "A warm cup and a bold plan will clear the path ahead.",
    "The lantern is dim, but your way is already known.",
    "A small kindness opens a large gate.",
    "Storms polish stones; so does challenge polish you.",
    "Your next message will carry unexpected luck.",
    "Follow the ink trail; the right answer is nearby.",
    "The dragon sleeps; your calm keeps it at peace.",
    "A new friend arrives when you least expect.",
    "Honor the silence, then speak with certainty.",
]

FORTUNE_HTML = """\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Midnight Fortune</title>
    <style>
      :root {
        color-scheme: dark;
        --ink: #0a0a0a;
        --ink-2: #141414;
        --ember: #b21b2c;
        --gold: #d4b066;
        --paper: #f3e8cf;
        --paper-2: #e7d9b7;
        --shadow: rgba(0, 0, 0, 0.55);
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Georgia", "Times New Roman", serif;
        background:
          radial-gradient(circle at 20% 20%, rgba(178, 27, 44, 0.25), transparent 55%),
          radial-gradient(circle at 80% 10%, rgba(212, 176, 102, 0.2), transparent 45%),
          linear-gradient(160deg, #050505 0%, #101010 55%, #070707 100%);
        color: #f2e9d8;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px 18px;
      }

      .frame {
        width: min(820px, 100%);
        border: 1px solid rgba(212, 176, 102, 0.35);
        padding: 36px;
        background: linear-gradient(180deg, rgba(10, 10, 10, 0.9), rgba(8, 8, 8, 0.98));
        box-shadow: 0 20px 45px var(--shadow);
      }

      .title {
        text-transform: uppercase;
        letter-spacing: 4px;
        font-size: 12px;
        color: var(--gold);
        margin-bottom: 18px;
      }

      h1 {
        margin: 0 0 18px;
        font-size: 38px;
        font-weight: 600;
      }

      .subtitle {
        margin: 0 0 28px;
        font-size: 16px;
        color: rgba(242, 233, 216, 0.75);
      }

      .fortune-card {
        position: relative;
        padding: 28px 28px 24px;
        background: linear-gradient(145deg, var(--paper), var(--paper-2));
        color: #2b2013;
        box-shadow: inset 0 0 0 2px rgba(178, 27, 44, 0.4),
          0 10px 25px rgba(0, 0, 0, 0.45);
        border-radius: 12px;
      }

      .fortune-card::before,
      .fortune-card::after {
        content: "";
        position: absolute;
        width: 42px;
        height: 42px;
        border: 2px solid rgba(178, 27, 44, 0.5);
      }

      .fortune-card::before {
        top: 8px;
        left: 8px;
        border-right: none;
        border-bottom: none;
      }

      .fortune-card::after {
        bottom: 8px;
        right: 8px;
        border-left: none;
        border-top: none;
      }

      .fortune-text {
        font-size: 22px;
        line-height: 1.5;
        margin: 0 0 20px;
      }

      .lucky {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        font-size: 14px;
        letter-spacing: 1px;
      }

      .lucky span {
        background: rgba(178, 27, 44, 0.12);
        border: 1px solid rgba(178, 27, 44, 0.35);
        padding: 6px 10px;
        border-radius: 999px;
      }

      .actions {
        margin-top: 24px;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }

      button {
        background: linear-gradient(135deg, #b21b2c, #7e0f1c);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f9f2e4;
        padding: 12px 18px;
        font-size: 14px;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      button:active { transform: scale(0.98); }

      button:hover {
        box-shadow: 0 10px 18px rgba(178, 27, 44, 0.35);
      }

      .seal {
        margin-top: 28px;
        font-size: 12px;
        color: rgba(242, 233, 216, 0.5);
        text-transform: uppercase;
        letter-spacing: 3px;
      }

      @media (max-width: 640px) {
        .frame { padding: 24px; }
        h1 { font-size: 30px; }
        .fortune-text { font-size: 19px; }
      }
    </style>
  </head>
  <body>
    <div class="frame">
      <div class="title">Temple of Nightfall</div>
      <h1>Midnight Fortune</h1>
      <p class="subtitle">
        A fortune revealed with the hush of incense and the crackle of a cookie.
      </p>
      <div class="fortune-card">
        <p class="fortune-text" id="fortuneText">Loading your fortune...</p>
        <div class="lucky" id="luckyNumbers"></div>
      </div>
      <div class="actions">
        <button id="newFortune">Crack Another</button>
      </div>
      <div class="seal">Fortune Cookie Ritual</div>
    </div>
    <script>
      const fortuneText = document.getElementById("fortuneText");
      const luckyNumbers = document.getElementById("luckyNumbers");
      const newFortune = document.getElementById("newFortune");

      function renderFortune(data) {
        fortuneText.textContent = data.fortune;
        luckyNumbers.innerHTML = "";
        data.lucky_numbers.forEach((number) => {
          const chip = document.createElement("span");
          chip.textContent = `Lucky ${number}`;
          luckyNumbers.appendChild(chip);
        });
      }

      async function fetchFortune() {
        fortuneText.textContent = "Listening to the wind...";
        const response = await fetch("/api/fortune");
        const data = await response.json();
        renderFortune(data);
      }

      newFortune.addEventListener("click", fetchFortune);
      fetchFortune();
    </script>
  </body>
</html>
"""

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Serve the fortune UI with a dark oriental theme."""
    return HTMLResponse(FORTUNE_HTML)

@app.get("/api/health")
def health():
    """Simple health check endpoint used by tooling."""
    return {"status": "ok"}

@app.get("/fortune", response_class=HTMLResponse)
def fortune_page() -> HTMLResponse:
    """Serve the themed fortune cookie page."""
    return HTMLResponse(FORTUNE_HTML)

@app.get("/api/fortune")
def fortune():
    """Return a randomized fortune and lucky numbers."""
    return {
        "fortune": random.choice(FORTUNES),
        "lucky_numbers": sorted(random.sample(range(1, 100), 6)),
    }

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        user_message = request.message
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": user_message}
            ]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")
