# AndroidWorld

[![Unittests](https://github.com/google-research/android_world/actions/workflows/pytest.yml/badge.svg)](https://github.com/google-research/android_world/actions/workflows/pytest.yml)

<p align="center">
<a href="https://google-research.github.io/android_world/">웹사이트</a> • 
<a href="https://arxiv.org/pdf/2405.14573">논문</a> • 
<a href="https://google-research.github.io/android_world/task_list.html">태스크 목록</a> • 
<a href="https://docs.google.com/spreadsheets/d/1cchzP9dlTZ3WXQTfYNhh3avxoLipqHN75v1Tb86uhHo/edit?gid=0#gid=0">리더보드</a>
</p>

![개요](assets/overview.png)

**AndroidWorld**는 자율 컴퓨터 제어 에이전트를 구축하고 벤치마크할 수 있는 환경입니다.
실제 Android 에뮬레이터에서 실행되며, 20개의 앱에 걸쳐 수작업으로 제작된 116개의 태스크를 포함하고 있습니다. 이 태스크들은 무작위로 생성된 매개변수를 통해 수백만 개의 고유한 변형을 만들어내는 **재현성 높은 벤치마크**입니다.

또한 AndroidWorld는 [Liu et al.](http://arxiv.org/abs/1802.08802)의 웹 벤치마크 MiniWoB++도 지원합니다.

**주요 특징:**

* 📝 실제 앱 20개에서 구성된 **116개의 다양한 태스크**
* 🎲 **동적 태스크 인스턴스화**로 수백만 개의 변형 생성 가능
* 🏆 **지속적인 보상 신호**를 통한 신뢰 가능한 평가
* 🐳 **Docker 실험적 지원** (2025년 6월 2일 기준)
* 🌐 수백만 개의 Android 앱 및 웹사이트에 접근 가능한 **개방형 환경**
* 💾 **가벼운 리소스 요구사항** (2GB 메모리, 8GB 디스크)
* 🔧 **확장 가능한 설계**로 새로운 태스크 및 벤치마크 쉽게 추가 가능
* 🖥️ 웹 기반 태스크인 **MiniWoB++와 통합**

[웹사이트](https://google-research.github.io/android_world/)에서 데모 영상을 확인하세요.

---

## 설치 방법

1. **Android 에뮬레이터 설정**

   1. [Android Studio](https://developer.android.com/studio) 다운로드
   2. AVD(Android Virtual Device) 생성

      * 디바이스: **Pixel 6**
      * 시스템 이미지: **Tiramisu, API Level 33**
      * 이름: **AndroidWorldAvd**
        [설정 영상 보기](https://github.com/google-research/android_world/assets/162379927/efc33980-8b36-44be-bb2b-a92d4c334a50)

2. **명령줄에서 에뮬레이터 실행**
   Android Studio UI가 아닌 CLI에서 실행해야 하며, 접근성 포워딩 앱과의 통신을 위해 `-grpc 8554` 플래그가 필요합니다.

   ```bash
   EMULATOR_NAME=AndroidWorldAvd
   ~/Library/Android/sdk/emulator/emulator -avd $EMULATOR_NAME -no-snapshot -grpc 8554
   ```

3. **\[선택사항] `conda` 환경 사용 권장**
   [Miniconda 설치](https://docs.anaconda.com/free/miniconda/miniconda-install/)

   ```bash
   conda create -n android_world python=3.11.8
   conda activate android_world
   ```

4. **AndroidWorld 설치 (Python 3.11 이상 필수)**

   ```bash
   git clone https://github.com/google-research/android_world.git
   cd ./android_world
   pip install -r requirements.txt
   python setup.py install
   ```

5. **모델 API 키 환경 변수 설정**

   ```bash
   export OPENAI_API_KEY=your-key
   export GCP_API_KEY=your-key
   ```

6. **`ffmpeg` 설치**

   ```bash
   # macOS
   brew install ffmpeg
   ```

---

## 빠른 시작

`minimal_task_runner.py` 스크립트를 실행하면 AndroidWorld의 기본 구조를 확인할 수 있습니다. 환경을 초기화하고 태스크를 설정한 뒤 기본 에이전트 M3A를 실행합니다.

```bash
python minimal_task_runner.py --task=ContactsAddContact
```

태스크를 지정하지 않으면 무작위로 선택됩니다.
*참고: Android 기본 앱이 아닌 오픈소스 앱을 실행하려면 `--perform_emulator_setup` 옵션을 추가하세요.*

---

## Docker 지원 (실험적 기능)

Docker를 통해 Android 환경과 서버를 컨테이너에서 실행할 수 있습니다.
**주의: 이 기능은 실험적이며 충분히 테스트되지 않았습니다.**

1. **Docker 이미지 빌드**

   ```bash
   docker build -t android_world:latest .
   ```

2. **컨테이너 실행**

   ```bash
   docker run --privileged -p 5000:5000 -it android_world:latest
   ```

   에뮬레이터와 FastAPI 서버가 시작되고, `http://localhost:5000`에서 접근 가능합니다.

3. **환경과 상호작용**
   `scripts/run_suite_on_docker.py` 스크립트를 참조하여 Docker 내 환경과 상호작용할 수 있습니다.

### Apple Silicon 사용자를 위한 주의사항

ARM 칩에서 `emulator` 패키지 설치에 문제가 있습니다. 이를 해결하려면 AMD64 아키텍처로 이미지를 빌드하세요:

```bash
docker buildx build --platform linux/amd64 -t android-emulator:latest .
```

Apple Silicon에서는 Docker 실행이 매우 느릴 수 있습니다 (리눅스 에뮬레이터 안에서 Android 에뮬레이터가 다시 실행되기 때문).

---

## 벤치마크 실행

📌 **2024년 11월 18일 기준, 각 태스크의 step 제한이 평균 사람 수행 시간의 약 2배로 조정되었습니다.**
[자세한 내용 보기](https://docs.google.com/spreadsheets/d/1KF-vY0Uy47o0mnursvs-HmS6hreU6U3rPrAjgEfjMK4/edit?usp=sharing)

```bash
python run.py \
  --suite_family=android_world \
  --agent_name=t3a_gpt4 \
  --perform_emulator_setup \
  --tasks=ContactsAddContact,ClockStopWatchRunning
```

* `--perform_emulator_setup`는 처음 실행 시 필수이며 앱 설치와 권한 설정에 시간이 걸릴 수 있습니다.
* `--tasks`는 특정 태스크만 실행할 때 사용합니다. 생략하면 전체 스위트를 실행합니다.
* `--checkpoint_dir` 플래그를 사용하면 중단된 실행을 재개할 수 있습니다.

---

## MiniWoB++ 태스크 실행

`--suite_family=miniwob`과 `--perform_emulator_setup`을 사용하면 AndroidWorld에서 MiniWoB++ 웹 기반 태스크를 실행할 수 있습니다.

이 방식의 장점은 입력 위젯들이 HTML이 아닌 Android 네이티브 위젯으로 렌더링된다는 점입니다.

<p align="center">
<img src="assets/miniwob.png" style="width:30%">
</p>

---

## 사용자 정의 에이전트 생성

1. [`EnvironmentInteractingAgent`](https://github.com/google-research/android_world/blob/main/android_world/agents/base_agent.py) 클래스를 상속받고 `step` 메서드를 구현하세요.
   각 루프마다 `step()`이 호출되며, 여기에서 스크린샷, UI 요소를 분석하고 액션을 선택하여 수행한 뒤 결과를 반환합니다.
   액션 예시는 [`json_action.py`](https://github.com/google-research/android_world/blob/main/android_world/env/json_action.py) 참고.

2. 에이전트를 `run.py`에 임포트하고, [`_get_agent()`](https://github.com/google-research/android_world/blob/main/run.py) 메서드에 이름과 함께 등록하세요.

3. 이후 `--agent_name` 플래그로 벤치마크 실행 시 해당 에이전트를 지정하면 됩니다.

---

## 새로운 태스크 추가하기

[태스크 추가 가이드](https://github.com/google-research/android_world/blob/main/docs/tasks_guide.md)를 참고하세요.

---

## 인용 안내 (Citation)

AndroidWorld를 사용한다면 아래 논문을 인용해 주세요:

```bibtex
@misc{rawles2024androidworlddynamicbenchmarkingenvironment,
  title={AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents},
  author={Christopher Rawles and Sarah Clinckemaillie and Yifan Chang and Jonathan Waltz and Gabrielle Lau and Marybeth Fair and Alice Li and William Bishop and Wei Li and Folawiyo Campbell-Ajala and Daniel Toyama and Robert Berry and Divya Tyamagundlu and Timothy Lillicrap and Oriana Riva},
  year={2024},
  eprint={2405.14573},
  archivePrefix={arXiv},
  primaryClass={cs.AI},
  url={https://arxiv.org/abs/2405.14573},
}
```

---

**이 프로젝트는 Google의 공식 지원 제품이 아닙니다.**

---
