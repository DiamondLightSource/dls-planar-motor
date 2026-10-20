import asyncio
from contextlib import asynccontextmanager
from typing import Any

from asyncua import ua
from asyncua.client.client import Client
from asyncua.common.node import Node
from asyncua.ua.attribute_ids import AttributeIds
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from dls_planar_motor.html_monitor_page import HTMLMonitorPage

PLC_URL = "opc.tcp://192.168.1.3:4840"
plc_client: Client | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global plc_client
    print(f"Connecting to PLC at {PLC_URL}...")
    plc_client = Client(url=PLC_URL, timeout=1500)
    try:
        await plc_client.connect()
        # Adapt dynamically to your exact library version's definition loader
        if hasattr(plc_client, "load_data_type_definitions"):
            await plc_client.load_data_type_definitions()  # Modern asyncua v1.x+
        elif hasattr(plc_client, "load_type_definitions"):
            await plc_client.load_type_definitions()
        print("Connected to PLC successfully!")
        yield
    finally:
        print("Disconnecting from PLC...")
        await plc_client.disconnect()


app: FastAPI = FastAPI(
    title="DLS Planar Motor Control API",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "WebSockets",
            "description": "🚀 **WebSocket Stream:** Connect using a WS client to "
            "`ws://localhost:8000/xbot1/status/stream` "
            "to receive real-time PLC updates.",
        }
    ],
)


@app.get("/monitor", response_class=HTMLResponse)
async def get_monitor_page():
    """Serves a clean diagnostic dashboard that connects automatically to WebSocket."""
    test_page = HTMLMonitorPage()
    html_content = test_page.get_page_content()
    return HTMLResponse(content=html_content)


#### GET STATUS ####


@app.get("/plc_health")
async def get_plc_health() -> dict[str, Any]:
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=PLC_Healthy_Flag")
        is_healthy = await node.read_value()
        return {"plc_healthy": is_healthy}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/status")
async def get_xbot1_status() -> dict[str, Any]:
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotStatus")
        xbot_status = await node.read_value()
        xbot1_status = xbot_status[0]
        return {"xbot1_status": xbot1_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/position")
async def get_xbot1_pos():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotPos")
        xbot_pos = await node.read_value()
        xbot1_pos = xbot_pos[0]
        return {"xbot1_pos": xbot1_pos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/xy_acc")
async def get_xbot1_xy_acc():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        xbot_xy_acc_vel = await node.read_value()
        xbot1_xy_acc_vel = xbot_xy_acc_vel[0].LongAxisAccVel
        return {"xbot1_xy_acc": xbot1_xy_acc_vel[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/xy_vel")
async def get_xbot1_xy_vel():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        xbot_xy_acc_vel = await node.read_value()
        xbot1_xy_acc_vel = xbot_xy_acc_vel[0].LongAxisAccVel
        return {"xbot1_xy_vel": xbot1_xy_acc_vel[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/z_vel")
async def get_xbot1_z_vel():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        xbot_z_vel = await node.read_value()
        xbot1_z_vel = xbot_z_vel[0].ShortAxisVel
        return {"xbot1_z_vel": xbot1_z_vel[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.get("/xbot1/exe_status")
async def get_xbot1_exe_status():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        xbot_exe_status = await node.read_value()
        xbot1_exe_status = xbot_exe_status[0].Execute
        return {"xbot1_exe_status": xbot1_exe_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


#### SET VALUES ####


class XBOT1PositionCommand(BaseModel):
    x: float
    y: float
    z: float


@app.post("/xbot1/demanded_position")
async def set_position(command: XBOT1PositionCommand):
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        # 1. Read the list of custom structures
        structure_list = await node.read_value()
        # 2. Access the first element in the list, then its .Pos attribute
        target_struct = structure_list[0]  # xbot1
        # 3. Modify the coordinates inside the target position array
        target_struct.Pos[0] = float(command.x)
        target_struct.Pos[1] = float(command.y)
        target_struct.Pos[2] = float(command.z)
        # 4. Wrap the entire list back up as an ExtensionObject array Variant
        variant_struct = ua.Variant(structure_list, ua.VariantType.ExtensionObject)
        data_value_container = ua.DataValue(variant_struct)
        # 5. Write the whole updated list back to the PLC
        await node.write_attribute(AttributeIds.Value, data_value_container)

        return {"status": "success", "detail": "Positions updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbots/activate")
async def activate_xbots():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotsActivate")
        # 1. Wrap True in an explicit Boolean Variant
        variant = ua.Variant(True, ua.VariantType.Boolean)
        # 2. Wrap it inside a DataValue CONTAINER but leave Timestamps blank/None
        data_value = ua.DataValue(variant)
        # 3. Write purely to the Value attribute ID
        # This completely strips out client-side timestamps that the PLC rejects
        await node.write_attribute(AttributeIds.Value, data_value)
        return {"status": "success", "detail": "Xbots activated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbots/deactivate")
async def deactivate_xbots():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotsActivate")
        variant = ua.Variant(False, ua.VariantType.Boolean)
        data_value = ua.DataValue(variant)
        await node.write_attribute(AttributeIds.Value, data_value)
        return {"status": "success", "detail": "Xbots deactivated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/exe_move")
async def xbot1_exe_move():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        structure_list = await node.read_value()
        target_struct = structure_list[0]
        target_struct.Execute = 1
        # Wrap the entire list back up as an ExtensionObject array Variant
        variant_struct = ua.Variant(structure_list, ua.VariantType.ExtensionObject)
        data_value_container = ua.DataValue(variant_struct)
        # Write the whole updated list back to the PLC
        await node.write_attribute(AttributeIds.Value, data_value_container)
        return {"status": "success", "detail": "Xbots moved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


@app.post("/xbot1/stop_move")
async def xbot1_stop_move():
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        structure_list = await node.read_value()
        target_struct = structure_list[0]
        target_struct.Stop = 1
        variant_struct = ua.Variant(structure_list, ua.VariantType.ExtensionObject)
        data_value_container = ua.DataValue(variant_struct)
        await node.write_attribute(AttributeIds.Value, data_value_container)
        return {"status": "success", "detail": "Xbots stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


class XBOT1LongAxisAccVelCommand(BaseModel):
    vel: float
    acc: float


@app.post("/xbot1/set_xy_acc_vel")
async def xbot1_set_xy_acc_vel(command: XBOT1LongAxisAccVelCommand):
    if plc_client is None:
        raise HTTPException(status_code=503, detail="PLC client is not initialized")
    try:
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")
        structure_list = await node.read_value()
        target_struct = structure_list[0]
        target_struct.LongAxisAccVel[1] = float(command.vel)  # 1 is vel
        target_struct.LongAxisAccVel[0] = float(command.acc)  # 0 is acc
        variant_struct = ua.Variant(structure_list, ua.VariantType.ExtensionObject)
        data_value_container = ua.DataValue(variant_struct)
        await node.write_attribute(AttributeIds.Value, data_value_container)
        return {"status": "success", "detail": "Xbots xy vel and acc set successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware failure: {e}") from e


class XbotSubHandler:
    """
    Handles incoming data change events from the OPC UA server
    and forwards them to the connected WebSocket client.
    """

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        # Get the current running event loop to thread-safely schedule tasks
        self.loop = asyncio.get_running_loop()

    def datachange_notification(
        self, _node: Node, val: Any, _data: ua.DataChangeNotification
    ) -> None:
        # This method is triggered by the asyncua client when the PLC value changes
        try:
            # Extract the 'Done' attribute from the first element of the collection
            xbot1_done = val[0].Done

            # Schedule the async WebSocket push from the synchronous callback context
            asyncio.run_coroutine_threadsafe(
                self.websocket.send_json({"xbot1_done": xbot1_done}), self.loop
            )
        except Exception as e:
            print(f"Error forwarding data change: {e}")


@app.websocket("/xbot1/status/stream")
async def stream_xbot1_status(websocket: WebSocket):
    if plc_client is None:
        await websocket.close(code=1013, reason="PLC client is not initialized")
        return

    await websocket.accept()

    try:
        # 1. Locate the new OPC UA Node (XbotMoveAbs)
        node = plc_client.get_node("ns=4;s=XbotMoveAbs")

        # 2. Create an OPC UA Subscription (Publishing interval in milliseconds)
        # Note: Ensure your handler class extracts '.Done' or the index if needed
        handler = XbotSubHandler(websocket)
        subscription = await plc_client.create_subscription(100, handler)  # type: ignore

        # 3. Subscribe to data changes on the XbotMoveAbs node
        handle = await subscription.subscribe_data_change(node)

        # 4. Keep the WebSocket connection alive until the client disconnects
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        print("API Client disconnected from stream.")
    except Exception as e:
        print(f"Hardware streaming failure: {e}")
    finally:
        # 5. Clean up subscriptions to avoid leaking resources on the PLC side
        try:
            await subscription.unsubscribe(handle)  # type: ignore
            await subscription.delete()  # type: ignore
        except NameError:
            pass  # Subscription was never successfully created

        # Ensure the socket safely closes if it hasn't already
        try:
            await websocket.close()
        except RuntimeError:
            pass  # Socket already closed
