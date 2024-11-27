import grpc
from concurrent import futures

import Protos.chat_pb2_grpc as chat_pb2_grpc
import Protos.chat_pb2 as chat_pb2

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def Chat(self, request_iterator, context):
        for message in request_iterator:
            print(f"[{message.user}]: {message.message}")
            yield chat_pb2.ChatMessage(user="Server", message=f"Echo: {message.message}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()