# gRPC-Study

Python으로 구현한 gRPC 양방향 스트리밍 채팅 예제입니다.  
Protocol Buffer 스키마 정의부터 코드 생성, 서버/클라이언트 구현까지 gRPC의 핵심 개념을 단계별로 학습할 수 있습니다.

---

## 목차

- [개요](#개요)
- [아키텍처](#아키텍처)
- [디렉터리 구조](#디렉터리-구조)
- [핵심 개념](#핵심-개념)
- [사전 요구사항](#사전-요구사항)
- [설치](#설치)
- [실행 방법](#실행-방법)
- [동작 흐름](#동작-흐름)
- [코드 설명](#코드-설명)

---

## 개요

| 항목 | 내용 |
|------|------|
| 언어 | Python 3 |
| 프레임워크 | gRPC (`grpcio`) |
| 직렬화 | Protocol Buffers v3 |
| 통신 방식 | Bidirectional Streaming RPC |
| 포트 | `50051` |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                        gRPC Channel                      │
│                                                          │
│  Client                                       Server     │
│  ┌──────────┐  stream ChatMessage  ┌────────────────┐   │
│  │          │ ──────────────────► │                │   │
│  │  client  │                      │  ChatService   │   │
│  │  .py     │ ◄────────────────── │  .Chat()       │   │
│  │          │  stream ChatMessage  │                │   │
│  └──────────┘                      └────────────────┘   │
│    localhost:50051                       [::]:50051       │
└─────────────────────────────────────────────────────────┘
```

클라이언트와 서버가 단일 연결에서 동시에 메시지를 송수신하는 **Bidirectional Streaming** 방식입니다.

---

## 디렉터리 구조

```
gRPC-Study/
├── Schema/                  # Protocol Buffer 스키마 정의
│   └── chat.proto           # ChatService, ChatMessage 정의
│
├── GenProtos/               # protobuf 코드 생성 스크립트
│   └── main.py              # .proto → Python 코드 자동 생성
│
├── Server/                  # gRPC 서버
│   ├── Protos/              # 생성된 protobuf 파일 (자동 생성)
│   │   ├── chat_pb2.py
│   │   ├── chat_pb2.pyi
│   │   └── chat_pb2_grpc.py
│   └── server.py            # 서버 구현
│
└── Client/                  # gRPC 클라이언트
    ├── Protos/              # 생성된 protobuf 파일 (자동 생성)
    │   ├── chat_pb2.py
    │   ├── chat_pb2.pyi
    │   └── chat_pb2_grpc.py
    └── client.py            # 클라이언트 구현
```

> `Server/Protos/`, `Client/Protos/` 디렉터리는 `GenProtos/main.py` 실행 시 자동 생성됩니다.

---

## 핵심 개념

### gRPC 통신 방식 4가지

| 방식 | 설명 | 이 프로젝트 |
|------|------|:-----------:|
| Unary | 요청 1 → 응답 1 | |
| Server Streaming | 요청 1 → 응답 N | |
| Client Streaming | 요청 N → 응답 1 | |
| **Bidirectional Streaming** | **요청 N → 응답 N** | **✓** |

### Protocol Buffer (proto3)

gRPC의 인터페이스 정의 언어(IDL)이자 직렬화 포맷입니다.  
언어 중립적으로 서비스 계약을 정의하고, 각 언어에 맞는 코드를 자동 생성합니다.

```proto
// 서비스 정의: 클라이언트↔서버 간 메시지를 스트리밍으로 주고받는 Chat RPC
service ChatService {
  rpc Chat (stream ChatMessage) returns (stream ChatMessage);
}

// 메시지 정의: 유저명과 메시지 내용
message ChatMessage {
  string user    = 1;
  string message = 2;
}
```

---

## 사전 요구사항

- Python 3.8 이상
- `pip` 또는 `uv`

---

## 설치

```bash
pip install grpcio grpcio-tools
```

또는 `uv` 사용 시:

```bash
uv add grpcio grpcio-tools
```

---

## 실행 방법

### 1단계: protobuf Python 코드 생성

```bash
cd GenProtos
python main.py
```

`Client/Protos/`, `Server/Protos/` 디렉터리에 아래 파일이 생성됩니다.

| 파일 | 역할 |
|------|------|
| `chat_pb2.py` | `ChatMessage` 메시지 직렬화/역직렬화 클래스 |
| `chat_pb2.pyi` | IDE 자동완성을 위한 타입 힌트 |
| `chat_pb2_grpc.py` | gRPC 서비스 스텁(Stub) 및 서비서(Servicer) |

### 2단계: 서버 실행

```bash
cd Server
python server.py
```

```
Server started on port 50051
```

### 3단계: 클라이언트 실행 (새 터미널)

```bash
cd Client
python client.py
```

```
Enter your username: alice
```

---

## 동작 흐름

```
[Client]                              [Server]
   │                                      │
   │── grpc.insecure_channel() ──────────►│
   │                                      │
   │  Enter username: alice               │
   │  Input: "Hello"                      │
   │── ChatMessage(user="alice",          │
   │              message="Hello") ──────►│
   │                                      │── print("[alice]: Hello")
   │◄── ChatMessage(user="Server",        │
   │               message="Echo: Hello") │
   │                                      │
   │  [Server]: Echo: Hello               │
   │                                      │
   │  Input: "How are you?"               │
   │── ChatMessage(...) ─────────────────►│
   │◄── ChatMessage(...) ─────────────────│
   │                                      │
   │  (빈 줄 입력 시 연결 종료)             │
```

- 클라이언트는 메인 스레드에서 메시지를 입력받아 전송합니다.
- 별도 스레드(`receiver_thread`)에서 서버 응답을 동시에 수신합니다.
- 서버는 수신한 메시지를 출력하고 `"Echo: {message}"` 형태로 응답합니다.

---

## 코드 설명

### `Schema/chat.proto`

서비스의 인터페이스 계약을 정의합니다.  
`stream` 키워드를 양방향에 모두 붙여 Bidirectional Streaming을 선언합니다.

### `GenProtos/main.py`

`grpc_tools.protoc` 명령을 Python에서 실행해 `.proto` 파일로부터 코드를 생성합니다.  
`Client/Protos/`, `Server/Protos/` 두 경로에 각각 생성하여 의존성을 분리합니다.

### `Server/server.py`

```python
class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def Chat(self, request_iterator, context):
        for message in request_iterator:
            print(f"[{message.user}]: {message.message}")
            yield chat_pb2.ChatMessage(user="Server", message=f"Echo: {message.message}")
```

- `request_iterator`: 클라이언트가 보내는 스트림을 이터레이터로 순회합니다.
- `yield`: 각 메시지에 대해 응답 스트림을 생성합니다.
- `ThreadPoolExecutor(max_workers=10)`: 동시 연결을 처리하는 스레드 풀입니다.

### `Client/client.py`

```python
def send_messages(stub):
    user = input("Enter your username: ")
    for line in iter(input, ""):        # 빈 줄 입력 시 종료
        yield chat_pb2.ChatMessage(user=user, message=line)

def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        responses = stub.Chat(send_messages(stub))

        # 수신을 별도 스레드에서 처리해 송수신을 동시에 진행
        receiver_thread = threading.Thread(target=receive_messages, args=(stub, responses))
        receiver_thread.start()
        receiver_thread.join()
```

- `send_messages`는 제너레이터로 구현되어 입력할 때마다 메시지를 스트리밍합니다.
- `iter(input, "")`: 빈 줄을 입력하면 루프가 종료됩니다.
- 수신 스레드를 분리해 입력 대기 중에도 서버 응답을 즉시 출력합니다.
