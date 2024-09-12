from fastapi import APIRouter, Request, WebSocket, Form 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from openai import OpenAI
from config.settings import get_settings

settings = get_settings()

router = APIRouter(
  prefix="/chat",
  tags=["Chat"],
)

client = OpenAI(
  api_key=settings.OPENAI_API_KEY
)

templates = Jinja2Templates(directory="templates")

chat_log = [
  {'role': 'system',
  'content': 'You are metal health doctor.'
  }
]

chat_responses = []

@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
  return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})

@router.websocket("/ws")
async def chat(websocket: WebSocket):
  await websocket.accept()

  while True:
    user_input = await websocket.receive_text()
    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    try:
      response = client.chat.completions.create(
        model=settings.OPENAI_MODEL_NAME,
        messages=chat_log,
        temperature=0.6,
        stream=True
      )

      ai_response = ''

      for chunk in response:
        if chunk.choices[0].delta.content is not None:
          ai_response += chunk.choices[0].delta.content
          await websocket.send_text(chunk.choices[0].delta.content)
      chat_responses.append(ai_response)

    except Exception as e:
      await websocket.send_text(f'Error: {str(e)}')
      break
  


@router.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):

  chat_log.append({'role': 'user', 'content': user_input})
  chat_responses.append(user_input)

  response = client.chat.completions.create(
    model=settings.OPENAI_MODEL_NAME,
    messages=chat_log,
    temperature=0.6
  )

  bot_response = response.choices[0].message.content
  chat_log.append({'role': 'assistant', 'content': bot_response})
  chat_responses.append(bot_response)

  return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})


@router.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
  return templates.TemplateResponse("image.html", {"request": request})


@router.post("/image", response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
  response = client.images.generate(
    prompt=user_input,
    n=1,
    size="512x512"
  )

  image_url = response.data[0].url
  return templates.TemplateResponse("image.html", {"request": request, "image_url": image_url})
