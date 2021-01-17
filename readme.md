Thanks David Montague!

> https://github.com/dmontagu/fastapi-utils

cbv.py 是普通CBV, 和WebSocketCBV的实现.

temp_router.py 一个简单的临时Router, 适合用于子路由. 需要自取.

(因为 APIRouter会对endpoint进行处理, 被Include进app的APIRouter时又会处理一次, 
TempRouter直接把处理阉割掉了, 仅作为信息临时存储, 用这个maybe可以省一点时间吧, 逃)

cbv_test.py & ws_test.py 两个测试用例


###代码比较少, 就不放到pypi上了, 直接copy下就好了