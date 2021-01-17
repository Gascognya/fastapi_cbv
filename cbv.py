import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union, get_type_hints
from pydantic import typing
from pydantic.typing import is_classvar
from starlette import routing, status
from starlette.responses import Response
from starlette.routing import Route, WebSocketRoute, Router
from starlette.types import ASGIApp, Message
from starlette.websockets import WebSocket
from starlette.endpoints import WebSocketEndpoint
from fastapi import Depends
from fastapi import params
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.routing import APIRoute, APIRouter, APIWebSocketRoute

# 如果使用, 可以尝试修正下包名
try:
    from .temp_router import TempRoute
except:
    TempRoute = None


class CBVRouter(Router):
    def __init__(
            self,
            path: str,
            group_name: str,
            *,
            tags: Optional[List[str]] = None,
            description: Optional[str] = None,
            summary: Optional[str] = None,
            routes: Optional[List[routing.BaseRoute]] = None,
            redirect_slashes: bool = True,
            default: Optional[ASGIApp] = None,
            dependency_overrides_provider: Optional[Any] = None,
            route_class: Type[APIRoute] = TempRoute or APIRouter,
            default_response_class: Optional[Type[Response]] = None,
            on_startup: Optional[Sequence[Callable]] = None,
            on_shutdown: Optional[Sequence[Callable]] = None,
    ) -> None:
        """
        :param group_name: 配置一个CBV的方法们独有的名字，方便标识。
        :param path: 整合参数，只能在此输入，必填
        :param tags: 整合参数，默认值是group_name
        :param description: 整合参数，只能在此输入
        :param summary: 整合参数，只能在此输入，默认值是group_name_方法名
        """
        super().__init__(
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )
        self.dependency_overrides_provider = dependency_overrides_provider
        self.route_class = route_class
        self.default_response_class = default_response_class

        self.path = path
        self.name = group_name
        self.tags = tags or [group_name]
        self.description = description
        self.summary = summary

    def method(
            self,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            summary: Optional[str] = None,
            tags: Optional[List[str]] = [],
            response_description: str = "Successful Response",
            dependencies: Optional[Sequence[params.Depends]] = None,
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Optional[Type[Response]] = None,
            name: Optional[str] = None,
            callbacks: Optional[List[APIRoute]] = None,
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            method = getattr(func, "__name__", None)
            assert method, "装饰器使用方式错误"
            assert method in ['get', 'post', 'put', 'delete', 'options', 'head', 'patch', 'trace'], \
                "请将方法名配置为' HTTP METHOD '中的一个"

            tags.extend(self.tags)

            route_class = self.route_class
            route = route_class(
                self.path,
                endpoint=func,
                response_model=response_model,
                status_code=status_code,

                tags=tags,
                description=self.description,
                methods=[method],
                operation_id=f'{self.name}_{self.path[1:]}_{method}',
                summary=summary or f'{self.name} _ {method}',

                dependencies=dependencies,
                deprecated=deprecated,
                response_description=response_description,
                responses=responses or {},
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class or self.default_response_class,
                name=name,
                dependency_overrides_provider=self.dependency_overrides_provider,
                callbacks=callbacks,
            )
            route.__class__ = APIRoute
            self.routes.append(route)

            return func

        return decorator


def API(router: CBVRouter):
    """
    例:
    router = CBVRouter(path="/user", group_name="User")

    @API(router)
    class TestClass:
        x: int = Depends(dependency)
        cx: ClassVar[int] = 1
        cy: ClassVar[int]

        def __init__(self, z: int = Depends(dependency)):
            self.y = 1
            self.z = z

        @router.method(response_model=int)
        async def get(self, d: int = 5) -> int:
            return self.cx + self.x + self.y + self.z

        @router.method(response_model=bool)
        def post(self) -> bool:
            return hasattr(self, "cy")

    1, 创建一个CBVRouter
    2, 使用@API(router)包装一个类
    3, 使用@router.method()来包装与HTTP方法同名的实例方法

    """

    def decorator(cls: Type):
        _get_method(cls, router)
        return cls

    return decorator


class WebSocketBase:
    """
    例:
    router = APIRouter()

    class WebSocketTest(WebSocketBase, path="/ws", router=router):
        async def on_receive(self, data: typing.Any) -> None:
            await self.websocket.send_text(f"Message text was: {data}")

    1, 继承于WebSocketBase类
    2, 同时在继承括号内部写入path与router两个参数, router为默认的APIRouter即可
    3, 重写on_connect, on_receive, on_disconnect等方法
    4, 重写__init__时请记得调用super
    5, 请不要随意重写_decode, decode, endpoint, __init_subclass__等内容
    """

    encoding = None
    _decode = WebSocketEndpoint.decode

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    def __init_subclass__(cls, **kwargs):
        router = kwargs.get("router", None)
        path = kwargs.get("path", None)
        endpoint = getattr(cls, "endpoint", None)
        assert isinstance(router, APIRouter), "缺少参数 router"
        assert isinstance(path, str), "缺少参数 path"
        assert endpoint, "缺少方法 endpoint"

        _update_cbv_class_init(cls)
        ws_cls = APIWebSocketRoute(path, endpoint)
        _update_endpoint_self_param(cls, ws_cls)
        router.routes.append(ws_cls)

    async def endpoint(self) -> None:
        assert self.websocket, "请在__init__()中配置正确的websocket对象"
        await self.on_connect()
        # ------------------------------
        close_code = status.WS_1000_NORMAL_CLOSURE
        try:
            while True:
                message = await self.websocket.receive()
                if message["type"] == "websocket.receive":
                    data = await self.decode(message)
                    await self.on_receive(data)
                    # ------------------------------
                elif message["type"] == "websocket.disconnect":
                    close_code = int(message.get("code", status.WS_1000_NORMAL_CLOSURE))
                    break
        except Exception as exc:
            close_code = status.WS_1011_INTERNAL_ERROR
            raise exc from None
        finally:
            await self.on_disconnect(close_code)
            # ------------------------------

    async def decode(self, message: Message) -> typing.Any:
        return await self._decode(message=message, websocket=self.websocket)

    async def on_connect(self) -> None:
        """Override to handle an incoming websocket connection"""
        await self.websocket.accept()

    async def on_receive(self, data: typing.Any) -> None:
        """Override to handle an incoming websocket message"""

    async def on_disconnect(self, close_code: int) -> None:
        """Override to handle a disconnecting websocket"""


def _get_method(cls, router):
    """抽离的公共代码"""
    # ------------修改__init__签名------------
    _update_cbv_class_init(cls)

    # ----------------抓取方法----------------
    function_members = inspect.getmembers(cls, inspect.isfunction)
    functions_set = set(func for _, func in function_members)

    def temp(r):
        if isinstance(r, (Route, WebSocketRoute)) and r.endpoint in functions_set:
            _update_endpoint_self_param(cls, r)
            return True
        return False

    router.routes = list(filter(temp, router.routes))


def _update_cbv_class_init(cls: Type[Any]) -> None:
    """
    重定义类的__init__(), 更新签名和参数
    """
    CBV_CLASS_KEY = "__cbv_class__"

    if getattr(cls, CBV_CLASS_KEY, False):
        return  # Already initialized

    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[1:]

    new_parameters = [
        x for x in old_parameters
        if x.kind not in
           (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]

    dependency_names: List[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=hint,
                **parameter_kwargs
            )
        )
    new_signature = old_signature.replace(parameters=new_parameters)

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__signature__", new_signature)
    setattr(cls, "__init__", new_init)
    setattr(cls, CBV_CLASS_KEY, True)


def _update_endpoint_self_param(cls: Type[Any], route: Union[Route, WebSocketRoute]) -> None:
    """
    调整endpoint的self参数，使其变为self=Depends(cls)
    这样每次处理依赖时，就可以实例化一个对象
    """
    old_endpoint = route.endpoint
    old_signature = inspect.signature(old_endpoint)
    old_parameters: List[inspect.Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(cls))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, "__signature__", new_signature)
