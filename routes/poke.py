import os
import logging
import base64
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv
from models.poke_card import Poke
from dictionaries.typing_prompts import card_type
from dictionaries.event_prompts import special_event


load_dotenv()

client = OpenAI()


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/poke")


def encode_image(file_path: str):
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image


@router.post("/image/create")
def create_card(poke: Poke):
    prompt = f"""
        Analyze the Image: Examine the first original image in the content list to understand its composition, color palette, and key elements.
        Study Studio Ghibli Style: Familiarize yourself with the distinctive features of Studio Ghibli's art style, including: - Soft, vibrant color palettes - Detailed backgrounds with a focus on nature - Expressive character designs with large, emotive eyes - Use of light and shadow to create depth
        Sketch the Transformation: Create a preliminary sketch that incorporates the Ghibli style elements into the original image.
        Apply Color and Texture: Use soft, vibrant colors typical of Studio Ghibli films. Pay attention to textures that mimic traditional animation techniques.
        Refine Details: Add intricate details to the background and characters, ensuring they align with the Ghibli aesthetic, ensure humans have their mouths are closed.
        {special_event[poke.special_event]["prompt"] if poke.special_event else card_type[poke.type]}
        Final Adjustments: Make any necessary adjustments to lighting, contrast, saturation to achieve a cohesive look, and make sure there is no added text.
    """

    print(prompt)

    input = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt,
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{encode_image(f'input/poke/{poke.image_name}')}",
                },
            ],
        }
    ]

    for image in special_event[poke.special_event]["images"]:
        input[0]["content"].append(
            {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{encode_image(image)}",
            }
        )
    print(input)

    response = client.responses.create(
        model="gpt-5",
        input=input,
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
        with open(f"output/poke/{poke.image_name}", "wb") as f:
            f.write(base64.b64decode(image_base64))
    else:
        print(response.output.content)


@router.post("/image/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open(f"input/poke/{file.filename}", "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Successful image upload!"}


@router.get("/image/get/outputs")
async def get_output_images() -> list:
    files = os.listdir("output/poke")
    return files


@router.get("/image/get/inputs")
async def get_input_images() -> list:
    files = os.listdir("input/poke")
    return files


@router.get("/image/get/static/{fileName}")
async def get_static_image(fileName: str) -> str:
    file_path = Path("output/poke") / fileName

    if not file_path.exists():
        raise HTTPException(status_code=500, detail={"File not found"})

    return FileResponse(file_path)
