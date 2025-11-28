from src.states.blog_state import BlogState
from langchain_core.messages import HumanMessage, AIMessage
from src.states.blog_state import Blog

class BlogNode:
    """
    A class to represent the blog node
    """
    
    def __init__(self, llm):
        self.llm = llm
        
    def title_creation(self, state: BlogState):
        if "topic" in state and state['topic']:
            prompt = """You are an SEO title expert. Generate ONE best compelling H1 blog title for the topic: {topic}.

                Incorporate primary keyword "{primary_keyword}" at the start or naturally. Use secondary keywords "{secondary_keywords}" where fitting.

                Rules for title:
                - Under 60 characters for SERP display
                - High CTR formulas: How-to, Ultimate Guide, Question, Numbered List, [2025/2026]
                - Power words: Ultimate, Proven, Best, Complete, Easy, Fast
                - Curiosity gap or benefit-driven
                - Unique, brandable, mobile-friendly

                Output ONLY the title itself. No quotes, no explanations."""
            
            # Fix: Use state values properly
            system_message = prompt.format(
                topic=state["topic"],
                primary_keyword=state.get("primary_keyword", state["topic"]),
                secondary_keywords=state.get("secondary_keywords", "")
            )
            response = self.llm.invoke(system_message)
            return {"blog": {"title": response.content.strip()}}

    def content_generation(self, state: BlogState):
        if "topic" in state and state["topic"] and "blog" in state and state["blog"].get("title"):
            prompt = """You are an expert SEO-optimized blog writer. Generate a COMPLETE blog post using this title: "{title}"

            Topic: {topic}

            Structure in FULL Markdown format:
            # {title} (H1 - keep exact)
            ## Introduction (200-300 words, hook + thesis)
            ## [4-6 H2 sections with H3 subheaders] (keyword-rich, scannable)
            - Use bullet points/lists
            - Short paragraphs (3 sentences max)
            - Bold **key phrases**
            ## Conclusion (summary + CTA)
            ## FAQs (5 questions/answers)

            SEO Rules:
            - Natural {primary_keyword} density 1-2%
            - Secondary keywords: {secondary_keywords}
            - 1500-2000 words total
            - Mobile-friendly, conversational tone
            - Suggest 4-6 images: ![Alt text](image-placeholder.jpg)
            - E-E-A-T compliant, value-first content

            Output ONLY the full Markdown blog. No explanations."""

            system_message = prompt.format(
                title=state["blog"]["title"],
                topic=state["topic"],
                primary_keyword=state.get("primary_keyword", ""),
                secondary_keywords=state.get("secondary_keywords", "")
            )
            response = self.llm.invoke(system_message)
            return {
                "blog": {
                    "title": state["blog"]["title"],
                    "content": response.content.strip()
                }
            }
        return state  # Pass through if missing data


    def translation(self, state: BlogState):
        blog_content = state["blog"]["content"]
        
        prompt = f"""
        Translate this blog to {state["current_language"]} while keeping the SAME structure.
        
        Respond as VALID JSON only with this exact schema:
        {{
            "title": "translated title here",
            "content": "full translated markdown content here"
        }}
        
        ORIGINAL:
        {blog_content}
        """
        
        messages = [HumanMessage(content=prompt)]
        
        # Use simple invoke + JSON parsing (no structured output)
        response = self.llm.invoke(messages)
        
        # Extract JSON from response
        import json
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            blog_data = json.loads(json_match.group())
        else:
            blog_data = {"title": "Translated Title", "content": response.content}
        
        return {
            "blog": {
                "title": blog_data["title"],
                "content": blog_data["content"]
            }
        }

    
    def route(self, state: BlogState):
        return {"current_language": state["current_language"]}
    
    def route_decision(self, state: BlogState):
        
        """
        Route the content to the respective translation function.
        """
        
        if state["current_language"] == "nepali":
            return "nepali"
        
        elif state["current_language"] == "french":
            return "french"

        else:
            return state["current_language"]