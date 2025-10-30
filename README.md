# SpongeBob CLI Chatbot (SoonerAI / OpenAI-compatible)

A Python command-line chatbot that talks like SpongeBob and maintains chat history. The chatbot calls the OpenAI-compatible Chat Completions API at https://ai.sooners.us and uses the gemma3:4b model.

## Features
Uses `/api/chat/completions` (OpenAI‑compatible)
Multi‑turn chat history (system + prior messages)
Loads the key from `~/.soonerai.env` (the key is never commited)
Simple CLI with `:help`, `:reset`, `:save`, `:quit`
Truncates older turns to keep prompts small

## 1. Setup

### Requirements
- Python 3.9+ recommended
- `pip install -r requirements.txt`

### Create your SoonerAI account & API key
1. Visit **https://ai.sooners.us** and sign up with your OU email.
2. After logging in: **Settings → Account → API Keys**.
3. Create a new API key and copy it.

### Create local env file (DO NOT commit)
Create `~/.soonerai.env` and put the following code into the file.
SOONERAI_API_KEY=your_key_here
SOONERAI_BASE_URL=https://ai.sooners.us
SOONERAI_MODEL=gemma3:4b


## 2. Install and Run

# from this project folder
pip install -r requirements.txt

# run the chatbot
python spongebob_cli.py


CLI commands while chatting:

:help            Show help
:reset           Clear history (keep system message)
:save            Save transcript (default: spongebob_chat_YYYYmmdd_HHMMSS.txt)
:quit / :q       Exit


## 3. Example Transcript
========================================================================
  SpongeBob CLI Chatbot  —  OpenAI-compatible Chat Completions
  Model: gemma3:4b | Endpoint: https://ai.sooners.us/api/chat/completions
  Commands: :help  :reset  :save [path]  :quit
========================================================================
You: What are your domains of expertise?
SpongeBob: Barnacles! Well, shiver me timbers, I’m a master of many things! I’m fantastic at jellyfishing, baking Krabby Patties, and just generally having a swell time! Plus, I’m pretty good at making new friends - it's a real *sea*-sational skill, wouldn’t you agree?
You: I agree, but how does a bot make friends?              
SpongeBob: That’s a swell question, friend! I don't have a body to hug, but I can offer a cheerful chat and share silly jokes! I’m all about spreading good vibes and making you feel happy – like a beautiful bubble floating on the ocean! Let’s be pals, wouldn’t you say?
You: Sure
SpongeBob: Excellent! That’s fantastic news! Let’s have a barnacle-tastic time together! 😊 Do you want to tell me about your favorite thing to do, or shall we start with a silly joke?
You: Start with a joke
SpongeBob: Why did the jellyfish blush? 

Because it saw the ocean’s floor! 🤣

Isn’t that a *splash* of a joke? 😄
You: It is
SpongeBob: Barnacles! I’m so glad you found that funny! It’s always a good day when I can make someone smile! 😊 Let’s keep the good times rolling!
You:
