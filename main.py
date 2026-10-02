import asyncio
import json
import websockets

# Automatic reaction ㊗️ to message

# ========== 配置区域 ==========
WS_URL = "ws://127.0.0.1:3001"
ACCESS_TOKEN = "Es.h_yVnTe5R2WZn"
TARGET_GROUP_ID = 562204345        # 只对这个群生效
TARGET_EMOJI_ID = "12951"            # 要贴的表情 ID（12951 = ㊗️）
# ==============================

class NapCatAutoReactor:
    def __init__(self, ws_url, token=""):
        self.ws_url = ws_url
        self.token = token
        self.ws = None
        self.echo_counter = 0

    async def connect_and_listen(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            self.ws = await websockets.connect(self.ws_url, additional_headers=headers)
            print(f"✅ 已连接: {self.ws_url}")
            print(f"🎯 监听群: {TARGET_GROUP_ID} | 自动贴表情 ID: {TARGET_EMOJI_ID}\n")

            async for raw_msg in self.ws:
                try:
                    data = json.loads(raw_msg)
                except json.JSONDecodeError:
                    continue

                # 跳过 API 响应
                if "echo" in data:
                    continue

                # 只处理群消息事件
                if data.get("post_type") == "message" and data.get("message_type") == "group":
                    group_id = data.get("group_id")
                    message_id = data.get("message_id")

                    # 只对指定群生效
                    if group_id != TARGET_GROUP_ID:
                        continue

                    sender = data.get("sender", {})
                    nickname = sender.get("nickname", "未知")
                    print(f"📨 群 {group_id} | {nickname} 发了一条消息 (ID: {message_id})")

                    # 立刻贴表情
                    await self.set_emoji_like(message_id, TARGET_EMOJI_ID)

        except websockets.ConnectionClosed:
            print("⚠️ WebSocket 连接已断开")
        except Exception as e:
            print(f"❌ 异常: {e}")

    async def set_emoji_like(self, message_id, emoji_id):
        """调用 set_msg_emoji_like API 给消息贴表情"""
        self.echo_counter += 1
        echo = f"react_{self.echo_counter}"

        request = {
            "action": "set_msg_emoji_like",
            "params": {
                "message_id": str(message_id),
                "emoji_id": str(emoji_id),
                "set": True
            },
            "echo": echo
        }
        await self.ws.send(json.dumps(request))
        print(f"   ✅ 已贴表情 {emoji_id} 到消息 {message_id}")


async def main():
    reactor = NapCatAutoReactor(WS_URL, ACCESS_TOKEN)
    await reactor.connect_and_listen()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 已停止")