from typing import ClassVar
from fastapi import Depends
from .cbv import API, CBVRouter


def dependency(num: int) -> int:
    return num


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
