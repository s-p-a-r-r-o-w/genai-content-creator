import os
import requests
from typing import Dict, TypedDict
from datetime import datetime
import base64
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langchain.prompts import PromptTemplate
from logger import setup_logger

# Load environment variables
load_dotenv()
logger = setup_logger("workflow")


class WorkflowState(TypedDict):
    topic: str
    blog_post: str
    image_url: str
    image_path: str
    word_count: int
    execution_time: float


class ContentWorkflow:
    def __init__(self, openrouter_api_key: str):
        self.openrouter_api_key = openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Create images directory
        self.images_dir = "generated_images"
        os.makedirs(self.images_dir, exist_ok=True)
    
    def generate_blog_post(self, state: WorkflowState) -> WorkflowState:
        """Generate blog post based on topic"""
        logger.info(f"Generating blog post for topic: {state['topic']}")
        
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="""
            Write a LinkedIn blog post about "{topic}".
            
            Requirements:
            - Exactly 230-270 words
            - Professional yet engaging tone
            - Include 3-5 relevant hashtags at the end
            - End with a clear call-to-action
            - Format for LinkedIn readability (short paragraphs, emojis where appropriate)
            
            Post:
            """
        )
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/content-workflow",
            "X-Title": "Content Workflow"
        }
        
        data = {
            "model": "meta-llama/llama-4-scout:free",
            "messages": [{
                "role": "user",
                "content": prompt.format(topic=state["topic"])
            }],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"API returned {response.status_code}: {response.text}")
                
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise Exception(f"Invalid API response: {result}")
                
            blog_post = result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            blog_post = f"""🚀 {state['topic'].title()}: A Game-Changer

The landscape is evolving rapidly, and {state['topic'].lower()} is at the forefront of this transformation.

Key insights:
• Innovation drives progress
• Adaptation is essential
• Success requires strategy
• Implementation matters most
• Results speak volumes

This shift represents more than just change—it's an opportunity to redefine how we approach challenges and create value.

The future belongs to those who embrace these developments and turn them into competitive advantages.

What's your experience with {state['topic'].lower()}? Share your thoughts below! 👇

#Innovation #Strategy #Growth #Leadership #Future"""

        words = blog_post.split()
        word_count = len(words)
        
        if word_count > 270:
            blog_post = ' '.join(words[:270])
            word_count = 270
        
        state["blog_post"] = blog_post
        state["word_count"] = word_count
        logger.info(f"Blog post generated successfully. Word count: {word_count}")
        return state
    
    def generate_image(self, state: WorkflowState) -> WorkflowState:
        """Generate image using the existing image_generator module"""
        logger.info(f"Generating image for topic: {state['topic']}")
        from image_generator import generate_and_save_image
        
        topic = state['topic']
        blog_content = state['blog_post']
        
        # Create LinkedIn-optimized prompt
        image_prompt = f"""Create a professional LinkedIn social media image (1080x1080) for: {topic}

Style: Modern, clean, business-appropriate
Colors: Professional palette (blues, grays, whites)
Elements: Abstract shapes, icons related to {topic}
Mood: Inspiring, professional

Based on content: {blog_content[:200]}...

Generate a visually appealing image without text overlay."""
        
        try:
            result = generate_and_save_image(image_prompt)
            
            if result["error"]:
                logger.error(f"Image generation error: {result['error']}")
                state["image_path"] = ""
                state["image_url"] = ""
            else:
                state["image_path"] = result["image_path"]
                state["image_url"] = result["image_path"]
                logger.info(f"Image generated successfully: {result['image_path']}")
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            state["image_path"] = ""
            state["image_url"] = ""
            
        return state
    

    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        workflow.add_node("generate_blog_post", self.generate_blog_post)
        workflow.add_node("generate_image", self.generate_image)
        
        workflow.add_edge(START, "generate_blog_post")
        workflow.add_edge("generate_blog_post", "generate_image")
        workflow.add_edge("generate_image", END)
        
        return workflow.compile()
    
    def run_workflow(self, topic: str) -> Dict:
        """Execute the complete workflow"""
        logger.info(f"Starting workflow for topic: {topic}")
        start_time = datetime.now()
        
        workflow = self.create_workflow()
        
        initial_state = WorkflowState(
            topic=topic,
            blog_post="",
            image_url="",
            image_path="",
            word_count=0,
            execution_time=0.0
        )
        
        result = workflow.invoke(initial_state)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        result["execution_time"] = execution_time
        
        logger.info(f"Workflow completed in {execution_time:.2f} seconds")
        return result