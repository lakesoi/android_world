import json
import time
import sys

from android_world.agents import base_agent
from android_world.env import adb_utils
from android_world.env import interface
from android_world.utils import file_utils


class AdbBroadcastAgent(base_agent.EnvironmentInteractingAgent):
    """Agent that delegates execution to an external Android process via adb."""

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


# android_world/agents/adb_broadcast_agent.py 중간 이후에 추가
import argparse
from android_world.env import env_launcher

def _run(goal: str, timeout: float, adb_path: str | None, console_port: int) -> None:
    env = env_launcher.load_and_setup_env(
        console_port=console_port,
        emulator_setup=False,
        adb_path=adb_path,
    )
    env.reset(go_home=True)
    agent = AdbBroadcastAgent(env, timeout=timeout)

    result = agent.step(goal)
    print("Result:", result.data.get("result"))
    env.close()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal", required=True, help="보낼 목표 문장")
    parser.add_argument("--timeout", type=float, default=30.0, help="결과 대기 시간(초)")
    parser.add_argument("--adb_path", default=None, help="adb 실행 파일 경로")
    parser.add_argument("--console_port", type=int, default=5554, help="에뮬레이터 콘솔 포트")
    args = parser.parse_args()
    _run(args.goal, args.timeout, args.adb_path, args.console_port)

if __name__ == "__main__":
    main()

