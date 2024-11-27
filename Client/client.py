import grpc
import threading

import Protos.chat_pb2_grpc as chat_pb2_grpc
import Protos.chat_pb2 as chat_pb2


def send_messages(stub):
    user = input("Enter your username: ")
    for line in iter(input, ""):
        yield chat_pb2.ChatMessage(user=user, message=line)


def receive_messages(stub, responses):
    try:
        for response in responses:
            print(f"[{response.user}]: {response.message}")
    except grpc.RpcError as e:
        print(f"Error: {e}")


def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        responses = stub.Chat(send_messages(stub))

        # Receive messages in a separate thread
        receiver_thread = threading.Thread(target=receive_messages, args=(stub, responses))
        receiver_thread.start()
        receiver_thread.join()


if __name__ == '__main__':
    main()