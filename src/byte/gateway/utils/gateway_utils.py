import inspect

from byte.gateway.protocol import RpcError, RpcRequest, RpcResponse
from byte.gateway.requests import GatewayRequest, Requests
from byte.support import Str


class GatewayUtils:
    """Gateway utility helper methods."""

    REQUEST_TYPES: dict[str, type[GatewayRequest]] = {
        Str.class_to_snake_case(cls.__name__): cls
        for _, cls in inspect.getmembers(Requests, inspect.isclass)
        if issubclass(cls, GatewayRequest) and cls is not GatewayRequest
    }

    @staticmethod
    def parse_request(rpc: RpcRequest) -> GatewayRequest:
        """Parse an RpcRequest into a typed GatewayRequest subclass.

        Args:
            rpc: The RPC request to parse.

        Returns:
            A GatewayRequest instance of the appropriate type.

        Raises:
            ValueError: If the method is unknown or params are invalid.
        """
        request_class = GatewayUtils.REQUEST_TYPES.get(rpc.method)
        if request_class is None:
            raise ValueError(f"Unknown method: {rpc.method}")

        params = rpc.params or {}
        try:
            return request_class(id=rpc.id, **params)
        except TypeError as exc:
            raise ValueError(f"Invalid params for {rpc.method}: {exc}") from exc

    @staticmethod
    def make_error_response(id: str | int | None, code: int, message: str) -> RpcResponse:
        """Build an RpcResponse carrying an RpcError for the given code and message.

        Args:
            id: The request id (or None if unavailable).
            code: The error code.
            message: The error message.

        Returns:
            An RpcResponse with the error.
        """
        return RpcResponse(
            id=id if id is not None else 0,
            error=RpcError(code=code, message=message),
        )
