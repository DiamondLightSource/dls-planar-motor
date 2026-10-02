from contextlib import asynccontextmanager

from asyncua import Client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

PLC_URL = "opc.tcp://192.168.1.3:4840"
plc_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global plc_client
    print(f"Connecting to PLC at {PLC_URL}...")
    plc_client = Client(url=PLC_URL, timeout=1500)
    try:
        await plc_client.connect()
        print("Connected to PLC successfully!")
        yield
    finally:
        print("Disconnecting from PLC...")
        await plc_client.disconnect()


app = FastAPI(title="DLS Planar Motor Control API", lifespan=lifespan)


@app.get("/plc_health")
async def get_plc_health():
    try:
        node = plc_client.get_node("ns=4;s=PLC_Healthy_Flag")
        is_healthy = await node.read_value()
        return {"plc_healthy": is_healthy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/status")
async def get_xbot1_status():
    try:
        node = plc_client.get_node("ns=4;s=XbotStatus")
        xbot_status = await node.read_value()
        xbot1_status = xbot_status[0]
        return {"xbot1_status": xbot1_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/x_position")
async def get_xbot1_x_pos():
    try:
        node = plc_client.get_node("ns=4;s=XbotPos.X")
        xbot_x_pos = await node.read_value()
        xbot1_x_pos = xbot_x_pos[0]
        return {"xbot1_x_pos": xbot1_x_pos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/y_position")
async def get_xbot1_y_pos():
    try:
        node = plc_client.get_node("ns=4;s=XbotPos.Y")
        xbot_y_pos = await node.read_value()
        xbot1_y_pos = xbot_y_pos[0]
        return {"xbot1_y_pos": xbot1_y_pos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/z_position")
async def get_xbot1_z_pos():
    try:
        node = plc_client.get_node("ns=4;s=XbotPos.Y")
        xbot_z_pos = await node.read_value()
        xbot1_z_pos = xbot_z_pos[0]
        return {"xbot1_z_pos": xbot1_z_pos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/xy_vel")
async def get_xbot1_xy_vel():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.LongAxisAccVel")
        xbot_xy_vel = await node.read_value()
        xbot1_xy_vel = xbot_xy_vel[0][1]  # !!!!
        return {"xbot1_xy_vel": xbot1_xy_vel}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/z_vel")
async def get_xbot1_z_vel():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.ShortAxisVel")
        xbot_z_vel = await node.read_value()
        xbot1_z_vel = xbot_z_vel[0][0]
        return {"xbot1_z_vel": xbot1_z_vel}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/xy_acc")
async def get_xbot1_xy_acc():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.LongAxisAccVel")
        xbot_xy_acc = await node.read_value()
        xbot1_xy_acc = xbot_xy_acc[0][0]
        return {"xbot1_xy_acc": xbot1_xy_acc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


class XBOT1PositionCommand(BaseModel):
    x: float
    y: float
    z: float


@app.post("/xbot1/demanded_position")
async def set_position(command: XBOT1PositionCommand):
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.Pos")
        current_structure = await node.read_value()
        current_structure[0][0] = command.x
        current_structure[0][1] = command.y
        current_structure[0][2] = command.z
        await node.write_value(current_structure)
        print("test")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbots/activate")
async def activate_xbots():
    try:
        node = plc_client.get_node("ns=4;s=XbotsActivate")
        # current_structure = await node.read_value()
        await node.write_value(1)  #!!??
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbots/deactivate")
async def deactivate_xbots():
    try:
        node = plc_client.get_node("ns=4;s=XbotsActivate")
        await node.write_value(0)  #!!??
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/exe_move")
async def xbot1_exe_move():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.Execute")
        current_structure = await node.read_value()
        current_structure[0] = 1
        await node.write_value(current_structure)  #!!??
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/stop_move")
async def xbot1_stop_move():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.Stop")
        current_structure = await node.read_value()
        current_structure[0] = 1
        await node.write_value(current_structure)  #!!??
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/set_xy_vel")
async def xbot1_set_xy_vel():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.LongAxisAccVel")
        current_structure = await node.read_value()
        current_structure[0][1] = 0.1  # this needs to be a command
        await node.write_value(current_structure)  #!!??
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/set_xy_acc")
async def xbot1_set_xy_acc():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.LongAxisAccVel")
        current_structure = await node.read_value()
        current_structure[0][0] = 1.0  # this needs to be a command
        await node.write_value(current_structure)  #!!??
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/set_xy_acc")
async def xbot1_set_z_vel():
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs.ShortAxisVel")
        current_structure = await node.read_value()
        current_structure[0][0] = 0.1  # this needs to be a command
        await node.write_value(current_structure)  #!!??

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e
