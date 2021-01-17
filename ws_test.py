import typing
from starlette.responses import HTMLResponse
from cbv import WebSocketBase
from temp_router import TempRouter

router = TempRouter()


class WebSocketTest(
    WebSocketBase,
    path="/ws",
    router=router
):
    async def on_receive(self, data: typing.Any) -> None:
        await self.websocket.send_text(f"Message text was: {data}")


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8888/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)


if __name__ == '__main__':
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)