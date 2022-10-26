from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
import socketio
import logging

class SocketioManager:
  def __init__(self, sio: socketio.AsyncServer) -> None:
    self._connections = []
    self._sio = sio
  
  async def sendData(self, id: str, event: str, data) -> bool:
    try:
      await self._sio.emit(event, data, to=id)
      return True
    except:
      logging.exception(f'Unable to send to {id}')
      return False
  
  async def sendDataMulti(self, ids: List[str], event: str, data) -> List[bool]:
    results = []
    for id in ids:
      # TODO: Allow data types other than dicts
      results.append(await self.sendData(id, event, dict(data)))
    return results
  
  # TODO: Add schema check for incoming data

class ConnectionManager:
  def __init__(self):
    self._connections: Dict[str, WebSocket] = dict()

  def addWebSocket(self, id: str, websocket: WebSocket): # For adding a web socket that has already been connected
    if id in self._connections:
      self.disconnect(id)
    self._connections[id] = websocket


  async def connect(self, id: str, websocket: WebSocket):
    await websocket.accept()
    self.addWebSocket(id, websocket)
  

  def disconnect(self, id: str) -> bool:
    if id in self._connections:
      self._connections[id].close()
      self._connections.pop(id)
      return True
    else:
      return False
  
  async def sendData(self, id: str, data) -> bool:
    try:
      websocket = self._connections[id]
    except KeyError:
      return False
    try:
      await websocket.send_json(data)
    except WebSocketDisconnect:
      self.disconnect(id)

  
  async def sendDataToMultiple(self, ids: List[str], data) -> List[str]:
    failed = list()
    for id in ids:
      try:
        self.sendData(id, data)
      except KeyError:
        failed.append(id)
        continue
      except WebSocketDisconnect:
        failed.append(id)
        continue
    return failed
      
  def cleanUp(self): # Send data to each connection, which will be removed from the list if there is no connection
    for id in self._connections:
      try:
        self.sendData(id, {'connection_test': True})
      except:
        continue
