from android_world.agents import base_agent
from android_world.env import adb_utils
from android_world.env import interface
from android_world.utils import file_utils
from android_world.env import env_launcher
import json
import time


class AdbBroadcastAgent(base_agent.EnvironmentInteractingAgent):
    BROADCAST_ACTION = "com.example.intent.TRIGGER_WORLD_STEP_REASONING"
    BROADCAST_RECEIVER = (
        "com.example.iotcore/com.example.adbinterface.receiver.WorldStepReasoningReceiver"
    )
    LOG_TAG = "AgentResult"
    RESULT_REMOTE_PATH = (
        "/storage/emulated/0/Documents/NodeInfoResponse/action_result.json"
    )

    def __init__(self, env: interface.AsyncEnv, timeout: float = 30.0):
        super().__init__(env, name="AdbBroadcastAgent")
        self._timeout = timeout

    def _broadcast_goal(self, goal: str) -> None:
        extras = {"goal": goal}
        adb_utils.send_android_intent(
            command="broadcast",
            action=self.BROADCAST_ACTION,
            env=self.env.controller,
            extras=extras,
        )

    def _wait_for_result(self) -> dict | None:
        adb_utils.issue_generic_request(["shell", "logcat", "-c"], self.env.controller)
        start = time.time()
        while time.time() - start < self._timeout:
            response = adb_utils.issue_generic_request(
                ["shell", "logcat", "-d", "-s", f"{self.LOG_TAG}:I", "*:S"],
                self.env.controller,
            )
            output = response.generic.output
            if output and self.LOG_TAG in output:
                try:
                    with file_utils.tmp_file_from_device(
                        self.RESULT_REMOTE_PATH, self.env.controller
                    ) as local_file:
                        with open(local_file, "r", encoding="utf-8") as f:
                            return json.load(f)
                except Exception as e:
                    return {"error": str(e)}
            time.sleep(1.0)
        return None

    def step(self, goal: str) -> base_agent.AgentInteractionResult:
        self._broadcast_goal(goal)
        result = self._wait_for_result()
        done = result is not None
        step_data = {"result": result}
        return base_agent.AgentInteractionResult(done, step_data)


# =====================
# 👇 여기가 직접 실행 부분
# =====================

def main():
    # ⬇️ 직접 설정값 입력
    GOAL = "와이파이 설정 열어줘"
    TIMEOUT = 30.0
    ADB_PATH = None         # 기본 adb 사용
    CONSOLE_PORT = 5554     # 에뮬레이터 포트

    env = env_launcher.load_and_setup_env(
        console_port=CONSOLE_PORT,
        emulator_setup=False,
        adb_path=ADB_PATH,
    )
    env.reset(go_home=True)

    agent = AdbBroadcastAgent(env, timeout=TIMEOUT)
    result = agent.step(GOAL)
    print("Result:", result.data.get("result"))

    env.close()


if __name__ == "__main__":
    main()
