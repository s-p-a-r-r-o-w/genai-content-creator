import os
import requests
import base64
from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from logger import setup_logger

load_dotenv()
logger = setup_logger("image_generator")

class ImageState(TypedDict):
    prompt: str
    image_path: str
    error: str

def generate_image(state: ImageState) -> ImageState:
    """Generate image using OpenRouter Gemini 2.5 Flash"""
    logger.info(f"Starting image generation with prompt: {state['prompt'][:50]}...")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-flash-image",
                "messages": [{
                    "role": "user",
                    "content": state['prompt']
                }],
                "modalities": ["image", "text"]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check for images in the response
            message = result['choices'][0]['message']
            if message.get('images'):
                for image in message['images']:
                    image_url = image['image_url']['url']
                    
                    if image_url.startswith('data:image'):
                        # Extract base64 image data
                        image_data = image_url.split(',')[1]
                        
                        # Save image locally
                        os.makedirs("generated_images", exist_ok=True)
                        filename = f"generated_images/image_{hash(state['prompt']) % 10000}.png"
                        
                        image_bytes = base64.b64decode(image_data)
                        with open(filename, 'wb') as f:
                            f.write(image_bytes)
                        
                        logger.info(f"Image saved successfully: {filename}")
                        return {"prompt": state["prompt"], "image_path": filename, "error": ""}
                
                logger.warning("No valid image data found in response")
                return {"prompt": state["prompt"], "image_path": "", "error": "No valid image data found"}
            else:
                logger.warning(f"No images in response: {message.get('content', '')[:100]}")
                return {"prompt": state["prompt"], "image_path": "", "error": f"No images in response: {message.get('content', '')[:100]}"}
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return {"prompt": state["prompt"], "image_path": "", "error": f"API Error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        logger.error(f"Image generation exception: {str(e)}")
        return {"prompt": state["prompt"], "image_path": "", "error": str(e)}

# Build LangGraph
workflow = StateGraph(ImageState)
workflow.add_node("generate", generate_image)
workflow.set_entry_point("generate")
workflow.add_edge("generate", END)

app = workflow.compile()

def generate_and_save_image(prompt: str) -> dict:
    """Main function to generate and save image"""
    result = app.invoke({"prompt": prompt, "image_path": "", "error": ""})
    return result

if __name__ == "__main__":
    # Example usage
    prompt = "A futuristic city skyline at sunset"
    result = generate_and_save_image(prompt)
    
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(f"Image saved to: {result['image_path']}")