"""
使用脚本需要在Python3环境下 推荐版本 python3.10
依赖库：
scapy            2.5.0
websocket-client 1.7.0

使用 pip 安装依赖
pip install scapy
pip install websocket-client

OBS需要开启 WebSocket: 工具-》Websocket服务器设置-》勾选开启Websoket服务器-》服务器端接口使用默认的4455-》取消勾选鉴权

使用：
1. 运行脚本
python obs_stream_setting.py
2. 直播伴侣或者任意 rtmp协议直播软件，中开始直播
3. 此时脚本会自动将 推流地址和key 绑定到 obs上
"""
import json
import websocket

from scapy.all import *

stream_obj = {}


def packe2json(pkt: Packet):
    js = {}
    for key in pkt.fields.keys():
        if key == "load":
            if "releaseStream" in str(pkt.fields[key]):
                stream = f"stream-{str(pkt.fields[key]).split("stream-")[-1].strip("'")}"
                if stream != stream_obj.get("key"):
                    js["stream"] = stream
            if "rtmp://" in str(pkt.fields[key]):
                rtmp = f"rtmp://{str(pkt.fields[key]).split("rtmp://")[-1].split("\\")[0]}"
                if rtmp != stream_obj.get("server"):
                    js["rtmp"] = rtmp
                
    if isinstance(pkt.payload, NoPayload):
        return js
    
    js = packe2json(pkt.payload)
    return js


def process_packet(packet):
    global stream_obj
    js = packe2json(packet)
    if js:
        if "rtmp" in js:
            print(f"成功获取到RTMP地址: {js["rtmp"]}")
            stream_obj["server"] = js.get("rtmp")
            if "key" in stream_obj:
                del stream_obj["key"]
        
        if "stream" in js:
            print(f"成功获取到stream-key: {js["stream"]}")
            stream_obj["key"] = js.get("stream")

            print("已经获取到推流密钥对, 准备替换OBS配置...")
            if "server" in stream_obj:
                obs_websocket_address = "ws://127.0.0.1:4455"
                ws = websocket.WebSocketApp(f"{obs_websocket_address}", on_message=osb_on_message)
                ws.run_forever()


def osb_on_message(ws: websocket, msg):
    msg = json.loads(msg)
    op = msg.get("op")
    d = msg.get("d")

    if op == 0:
        ws.send(json.dumps({
            "op": 1,
            "d": {
                "rpcVersion": 1, 
                "eventSubScriptons": (1<<16)
            }
        }))

        # 发送更改请求
        ws.send(json.dumps({
            "op": 6, 
            "d": {
                "requestType": "SetStreamServiceSettings", 
                "requestId": str(uuid.uuid4()),
                "requestData": {
                    "streamServiceType": "rtmp_custom",
                    "streamServiceSettings": {
                        "server": stream_obj["server"],
                        "key": stream_obj["key"]
                    }
                }
            }
        }))
    elif op == 2:
        print("成功建立OBS通信")

    elif op == 7 and d["requestType"] == "SetStreamServiceSettings":
        if d["requestStatus"]["code"] == 100:
            print("替换推流码成功")
        else:
            print("替换推流码异常: 请人工检查是否正确")

        ws.close()


sniff(prn=process_packet, store=0)
