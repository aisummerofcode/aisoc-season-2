from grpc import StatusCode
# from grcp_interceptor.exceptions import NotFound, GrpcException
from src.pb.server_pb2_grpc import AgenticServerServicer
from src.pb.server_pb2 import ChatRequest,ChatResponse,HealthCheckRequest,HealthCheckResponse
from src.application.chatdatamodel import ChatRequest

class AgenticServerBaseService(AgenticServerServicer):

    def Chat(self,request,context):
        try:
            chatRequest = ChatRequest(
                name = request.name,
                message= request.message,
                location=request.location
            )
            print("chatRequest came here",chatRequest)
            # your chatbot logic happened here
            call_agent(chatRequest)
            return ChatResponse(status=200, message="hello")
        except Exception as e:
            print(e)
            # raise GrpcException(
            #     status_code = StatusCode.INTERNAL,
            #     details=f"Internal server error occurred:{e}"
            # )

    def HealthCheck(self, request, context):
        return HealthCheckResponse(status="healthy")
        