# dwm1001_ROS2
### 💾 UWB 보드(dwm1001-dev) 초기 HW/SW 셋팅
1. [여기](https://www.qorvo.com/products/p/DWM1001-DEV#documents)에서 **DWM1001C Software and Documentation Pack** 을 다운.

2. **DWM1001-Firmware-User-Guide.pdf** (3장 참고) 와
   **DWM1001_Gateway_Quick_Deployment_Guide.pdf** (1~3장 참고) 에 따라 dwm1001-dev 초기셋팅(tag, anchor 지정)을 진행.

3. **DWM1001-API-Guide.pdf** (6.40 aurs 참고) 하여 tag 수신 hz 셋팅

4. Android 태블릿 앱 **DRTLS** 에서(APK로 다운 가능) tag와 anchor를 network로 묶고, 아래 ROS2 publisher 만들기 진행.

### 📁 파일 트리 구조
```plaintext
~/ros2_ws/
├── install/
├── build/
└── src/
    ├── dwm1001.py                         # dwm1001 코드 파일 복붙
    └── uwb_visualizer/                    # ROS2 패키지 (예: UWB 태그 publisher)
         ├── package.xml
         ├── setup.py                      # minor 수정 필요
         ├── launch/
         │    └── multi_tag.launch.py      # multi_tag.launch.py 코드 파일 복붙
         └── uwb_visualizer/
              ├── __init__.py
              └── uwb_tag_publisher.py     # uwb_tag_publisher.py 코드 파일 복붙
```
### :mag: ROS publisher + launch 파일 만들기
워크스페이스 디렉터리 생성
터미널에서 아래 명령어를 입력합니다.
```bash
mkdir -p ~/ros2_ws/src
```
ROS2 Python 패키지 생성
"uwb_visualizer"라는 이름의 패키지를 생성합니다. 이 패키지는 rclpy와 geometry_msgs에 의존합니다.
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python uwb_visualizer --dependencies rclpy geometry_msgs
```
생성 후 디렉터리 구조는 다음과 같습니다:
```plaintext
~/uwb_visualizer/      # ROS2 패키지
     ├── package.xml
     ├── setup.cfg
     ├── setup.py
     ├── resource/
     │   └── uwb_visualizer
     └── uwb_visualizer/
          ├── __init__.py
```
패키지 소스 폴더로 이동
```bash
cd ~/ros2_ws/src/uwb_visualizer/uwb_visualizer
```
파일 추가 (uwb_tag_publisher.py)
```
~/uwb_visualizer/      # ROS2 패키지
     ├── package.xml
     ├── setup.cfg
     ├── setup.py
     ├── resource/
     │   └── uwb_visualizer
     └── uwb_visualizer/
          ├── __init__.py
          └── uwb_tag_publisher.py
```

워크스페이스 src로 이동
```bash
cd ~/ros2_ws/src
```
파일 추가 (dwm1001.py) [원본🔗](https://github.com/the-hive-lab/pydwm1001/tree/main)
```
~/ros2_ws/
├── install/
├── build/
└── src/
    ├── dwm1001.py        # dwm1001 코드 파일 복붙
    └── uwb_visualizer/
```

launch 파일을 위한 폴더를 생성
```bash
mkdir ~/ros2_ws/src/uwb_visualizer/launch
```
다수의 tag 데이터를 동시에 publish하기 위한 노드 launch 파일 추가 (multi_tag.launch.py)

launch 파일을 추가한 파일 트리는 다음과 같습니다.
```plaintext
└── src/
    ├── dwm1001.py                         
    └── uwb_visualizer/                    
         ├── package.xml
         ├── setup.py                      
         ├── launch/
         │    └── multi_tag.launch.py    # multi_tag.launch.py 코드 파일 복붙
```    

패키지 루트 디렉토리로 이동
```bash
cd ~/ros2_ws/src/uwb_visualizer
```
`setup.py` 파일에서 launch 폴더 포함하도록 & entry_points 항목 수정

launch 폴더 포함하도록 파일 내 data_files 부분에 아래 내용을 추가합니다.
```python
data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/multi_tag.launch.py']),
    ],
```
파일 내 entry_points 부분에 아래 내용을 추가합니다.
```python
entry_points={
    'console_scripts': [
        'uwb_tag_publisher = uwb_visualizer.uwb_tag_publisher:main'
    ],
},
```
여기서 `'uwb_tag_publisher'`는 실행 시 사용할 명령어 이름이며,
`uwb_visualizer.uwb_tag_publisher:main`은 패키지 내의 모듈 경로와 `main()` 함수를 지정합니다.

워크스페이스 루트로 이동
```bash
cd ~/ros2_ws
```
colcon build 실행
```bash
colcon build --symlink-install
```
빌드가 완료되면 아래 명령어를 실행합니다.
```bash
source install/setup.bash
```
이 명령어를 실행해야 새로 빌드된 패키지와 노드가 ROS2에서 인식됩니다(`gedit ~/.bashrc`에 추가를 추천).

### 🖥️ 노드 실행 및 결과 확인
노드 실행
터미널에서 아래 명령어를 실행합니다.
```bash
ros2 run uwb_visualizer multi_tag.launch.py
```
이 명령어는 `setup.py`에 등록한 entry point를 통해 `main()` 함수를 호출하여 노드를 실행합니다.
노드가 실행되면 /dev/ttyACM0 ~ /dev/ttyACM3 시리얼 포트를 통해 실제 UWB 태그 위치 데이터를 읽어오며, 주기적으로 토픽 /uwb_tag0 ~ /uwb_tag3 을 통해 메세지를 publish하게 됩니다.

터미널에서 아래 명령어로 실제 연결된 시리얼 포트가 무엇인지 확인하세요(ttyUSB0로 연결될 수 있음):
```bash
ls /dev/tty*
```
만약 시리얼 포트가 ttyACM0 ~ ttyACM3 가 아니라면 `multi_tag.launch`에서 **parameters**를 수정하고 다시 빌드하세요.

다른 터미널을 열고 환경 설정을 다시 적용합니다.
```bash
source ~/ros2_ws/install/setup.bash
```
그런 후, 아래 명령어로 publish된 토픽 메시지를 확인합니다.
```bash
ros2 topic echo /uwb_tag
```
이 명령어를 통해 실제 태그 위치가 포함된 PoseStamped 메시지가 출력되는지 확인할 수 있습니다.

```bash
ros2 run uwb_visualizer uwb_tag_publisher --ros-args -p usb_port:=/dev/ttyACM0 -p topic_name:=/uwb_tag1
ros2 run uwb_visualizer uwb_tag_publisher --ros-args -p usb_port:=/dev/ttyACM1 -p topic_name:=/uwb_tag2
ros2 run uwb_visualizer uwb_tag_publisher --ros-args -p usb_port:=/dev/ttyACM2 -p topic_name:=/uwb_tag3
ros2 run uwb_visualizer uwb_tag_publisher --ros-args -p usb_port:=/dev/ttyACM3 -p topic_name:=/uwb_tag4
```

