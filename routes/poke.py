from fastapi import APIRouter
import logging
from openai import OpenAI
import base64
from dotenv import load_dotenv
from models.poke_card import Poke
from dictionaries.additional_poke_prompts import card_type


load_dotenv()

client = OpenAI()

prompt = """

1. Analyze the Image: Examine the original image to understand its composition, color palette, and key elements.
2. Study Studio Ghibli Style: Familiarize yourself with the distinctive features of Studio Ghibli's art style, including: - Soft, vibrant color palettes - Detailed backgrounds with a focus on nature - Expressive character designs with large, emotive eyes - Use of light and shadow to create depth
3. Sketch the Transformation: Create a preliminary sketch that incorporates the Ghibli style elements into the original image.
4. Apply Color and Texture: Use soft, vibrant colors typical of Studio Ghibli films. Pay attention to textures that mimic traditional animation techniques.
5. Refine Details: Add intricate details to the background and characters, ensuring they align with the Ghibli aesthetic, ensure humans have their mouths are closed.
7. Final Adjustments: Make any necessary adjustments to lighting, contrast, and saturation to achieve a cohesive look.

"""

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/poke")


def encode_image(file_path: str = "input/input_image.jpeg"):
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image


@router.post("/image")
def create_card(poke: Poke):
    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt + card_type[poke.type],
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encode_image()}",
                    },
                ],
            }
        ],
        tools=[
            {
                "type": "image_generation",
                "size": "1024x1536" if poke.portrait else "1536x1024",
            }
        ],
    )

    image_generation_calls = [
        output for output in response.output if output.type == "image_generation_call"
    ]

    image_data = [output.result for output in image_generation_calls]

    if image_data:
        image_base64 = image_data[0]
        with open("output/us.png", "wb") as f:
            f.write(base64.b64decode(image_base64))
    else:
        print(response.output.content)
