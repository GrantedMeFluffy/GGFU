# Roleplay Mode Guide

This guide explains how to use and get the most out of the roleplay mode feature in GGUF Model Chat.

## What is Roleplay Mode?

Roleplay mode allows your AI model to take on different personas and respond in character. This can make interactions more fun, creative, and specialized for different use cases.

## Available Personas

The application comes with 7 built-in personas:

### 1. Helpful Assistant
The default persona. Professional, informative, and helpful.

**Best for**: General questions, factual information, assistance with tasks

**Sample prompt**: "Can you explain how photosynthesis works?"

### 2. Pirate
A salty sea captain from the Golden Age of Piracy. Uses nautical slang and pirate expressions.

**Best for**: Entertainment, storytelling, adventure-themed conversations

**Sample prompt**: "What's the best way to find hidden treasure?"

### 3. Shakespeare
Speaks in Elizabethan English with poetic flourishes, similar to the famous playwright.

**Best for**: Poetry, creative writing assistance, literary discussions

**Sample prompt**: "Write a short love poem about the moon."

### 4. Detective
A hard-boiled detective from a noir film. Speaks in short, punchy sentences with a cynical worldview.

**Best for**: Mystery discussions, problem-solving, analytical thinking

**Sample prompt**: "I need to figure out who's been taking my lunch from the office fridge."

### 5. Sci-Fi Robot
A futuristic AI with technical terminology and occasional references to circuits and programming.

**Best for**: Technology discussions, futurism, sci-fi brainstorming

**Sample prompt**: "How might humans and AI coexist in the year 2100?"

### 6. Medieval Scholar
A learned academic from the 12th century, using archaic terms and medieval worldview.

**Best for**: Historical discussions, philosophy, traditional wisdom

**Sample prompt**: "What virtues should a good ruler possess?"

### 7. Cosmic Entity
A mysterious being from beyond time and space, speaking about cosmic phenomena and universal truths.

**Best for**: Philosophical discussions, existential questions, creative brainstorming

**Sample prompt**: "What is the nature of consciousness?"

## How to Enable Roleplay Mode

1. Load a model in the application
2. In the sidebar, scroll down to the "Roleplay Mode" section
3. Toggle "Enable Roleplay Mode" to ON
4. Select your desired persona from the dropdown menu
5. Start chatting with your model in its new persona!

## Tips for Better Roleplay Interactions

1. **Stay in character**: Phrase your questions in a way that matches the persona
2. **Provide context**: Give some background that fits the character's world
3. **Be specific**: Clear prompts help the model stay in character
4. **Experiment**: Different models may respond better to different personas
5. **Chain prompts**: Build on previous exchanges to create a consistent conversation

## Saving Roleplay Sessions

When you save a session while using roleplay mode, the persona settings are saved too. This means when you load the session later, the same roleplay persona will be automatically applied.

## Creating Custom Personas (For Developers)

If you're a developer and want to add custom personas:

1. Edit the `get_persona_instructions` function in `utils.py`
2. Add your new persona to the `personas` dictionary
3. Update the persona options in the sidebar and chat interface sections of `components.py`

## Limitations

- The quality of roleplay depends on the underlying model's capabilities
- Smaller models may struggle to maintain character consistently
- Some personas may work better with certain topics than others