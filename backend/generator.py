# backend/generator.py
import re

# Clean and extract key info from context
def clean_context(context: str) -> str:
    # Remove extra whitespace and truncate
    return ' '.join(context.strip().split()[:50]) + '...'

# Generate message using templates and tone logic
def generate_message(service: str, tone: str, location: str, context: str) -> str:
    context = clean_context(context)
    
    # Default values
    service = service.strip() or "this service"
    location = location.strip() or "your area"
    
    # Tone-based templates
    tone_templates = {
        "professional": (
            f"Hi, I came across your request regarding {context}. "
            f"I'm a {service} based in {location} and have helped others in similar situations. "
            "I'd be happy to discuss how I can support you — let me know if you'd be open to a quick chat."
        ),
        "friendly": (
            f"Hey, I saw you were looking into {context} — I'm a {service} here in {location}, "
            "and I've helped several clients with this exact thing. "
            "If you're still looking, I'd love to help out!"
        ),
        "urgent": (
            f"Hi, I saw your note about {context}. As a {service} in {location}, "
            "I understand how time-sensitive this can be. "
            "I'm available right away and can help resolve this quickly. Let me know if you'd like to connect."
        ),
        "consultative": (
            f"Thanks for sharing your thoughts on {context}. As a {service} specialist in {location}, "
            "I've found that many clients face similar challenges. "
            "There are a few proven approaches that could help — happy to share some insights if you're interested."
        ),
        "short": (
            f"Hi — I'm a {service} in {location}. Saw your post about {context}. "
            "I can help. Let me know if you'd like to connect."
        ),
        "detailed": (
            f"Hi, I came across your inquiry about {context}. "
            f"My name is Alex, and I'm a professional {service} serving clients in {location} and beyond. "
            "Over the past few years, I've successfully resolved similar issues for multiple customers. "
            "I’d love to learn more about your needs and see how I can assist. "
            "Would you be open to a brief 10-minute call this week?"
        ),
        "default": (
            f"Hi, I saw you were looking for help with {context}. "
            f"I'm a {service} based in {location} and would love to support you. "
            "Let me know if you're open to a quick conversation."
        )
    }

    # Use tone or fallback to default
    template = tone_templates.get(tone.lower().strip(), tone_templates["default"])
    
    # Replace placeholders (if any)
    template = template.replace("{service}", service)
    template = template.replace("{location}", location)
    template = template.replace("{context}", context)
    
    return template
