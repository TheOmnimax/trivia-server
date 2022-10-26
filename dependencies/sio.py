import socketio

from constants.constants import origins
from dependencies.websocket import SocketioManager

sio = socketio.AsyncServer(
  async_mode='asgi',
  cors_allowed_origins=origins
  )
socket_app = socketio.ASGIApp(sio)

socket_manager = SocketioManager(sio)