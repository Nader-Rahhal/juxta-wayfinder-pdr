import asyncio
import websockets
import json
import numpy as np
from collections import deque
import dataclasses
from typing import Dict

@dataclasses.dataclass
class IMUData:
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0
    acc_x: float = 0.0
    acc_y: float = 0.0
    acc_z: float = 9.81  # Default to gravity
    
    def to_dict(self) -> Dict[str, float]:
        return dataclasses.asdict(self)
        
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
        
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'IMUData':
        return cls(**data)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'IMUData':
        return cls.from_dict(json.loads(json_str))
        
    def to_array(self) -> list:
        return [self.gyro_x, self.gyro_y, self.gyro_z,
                self.acc_x, self.acc_y, self.acc_z]

class PDRServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.imu_buffer = deque(maxlen=100)
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_heading = 0.0

    async def handle_client(self, websocket):  # Removed 'path' parameter
        try:
            print("Client connected")
            async for message in websocket:
                try:
                    # Parse IMU data using IMUData class
                    imu_data = IMUData.from_json(message)
                    
                    # Print the received data
                    print("\nReceived IMU Data:")
                    print(f"Gyroscope (x,y,z): {imu_data.gyro_x:.3f}, {imu_data.gyro_y:.3f}, {imu_data.gyro_z:.3f}")
                    print(f"Accelerometer (x,y,z): {imu_data.acc_x:.3f}, {imu_data.acc_y:.3f}, {imu_data.acc_z:.3f}")
                    
                    # Store in buffer
                    self.imu_buffer.append(imu_data)
                    
                    # Send a simple acknowledgment back
                    response = {
                        "status": "received",
                        "timestamp": str(asyncio.get_event_loop().time())
                    }
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    print("Error: Invalid JSON received")
                    print(f"Raw message: {message}")
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        except Exception as e:
            print(f"Error in handle_client: {str(e)}")

    async def start_server(self):
        print(f"Starting PDR server on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # run forever

async def main():
    server = PDRServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())