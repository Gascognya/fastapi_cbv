from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type, Union
from starlette import routing
from starlette.responses import Response
from starlette.routing import get_name
from starlette.types import ASGIApp
from fastapi import params
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.routing import APIRoute, APIRouter


class TempRoute:
    def __init__(
            self,
            path: str,
            endpoint: Callable,
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            name: Optional[str] = None,
            methods: Optional[Union[Set[str], List[str]]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Optional[Type[Response]] = None,
            dependency_overrides_provider: Optional[Any] = None,
            callbacks: Optional[List["APIRoute"]] = None,
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name
        if methods is None:
            methods = ["GET"]
        self.methods = set([method.upper() for method in methods])
        self.response_model = response_model
        self.status_code = status_code
        self.tags = tags or []
        if dependencies:
            self.dependencies = list(dependencies)
        else:
            self.dependencies = []
        self.summary = summary
        self.description = description
        self.response_description = response_description
        self.responses = responses or {}
        self.deprecated = deprecated
        self.operation_id = operation_id
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none
        self.include_in_schema = include_in_schema
        self.response_class = response_class
        assert callable(endpoint), "An endpoint must be a callable"
        self.dependency_overrides_provider = dependency_overrides_provider
        self.callbacks = callbacks


class TempRouter(APIRouter):
    def __init__(
            self,
            routes: Optional[List[routing.BaseRoute]] = None,
            redirect_slashes: bool = True,
            default: Optional[ASGIApp] = None,
            dependency_overrides_provider: Optional[Any] = None,
            route_class: Type[TempRoute] = TempRoute,
            default_response_class: Optional[Type[Response]] = None,
            on_startup: Optional[Sequence[Callable]] = None,
            on_shutdown: Optional[Sequence[Callable]] = None,
    ) -> None:
        super().__init__(
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            default_response_class=default_response_class
        )

    def add_api_route(
            self,
            path: str,
            endpoint: Callable,
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            methods: Optional[Union[Set[str], List[str]]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Optional[Type[Response]] = None,
            name: Optional[str] = None,
            route_class_override: Optional[Type[APIRoute]] = None,
            callbacks: Optional[List[APIRoute]] = None,
    ) -> None:
        route_class = route_class_override or self.route_class
        route = route_class(
            path,
            endpoint=endpoint,
            response_model=response_model,
            status_code=status_code,
            tags=tags or [],
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses or {},
            deprecated=deprecated,
            methods=methods,
            operation_id=operation_id,
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
