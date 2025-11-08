from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from syncitvid.users.api.views import UserViewSet
from syncitvid.core.views import RoomViewset
router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("rooms",RoomViewset)

app_name = "api"
urlpatterns = router.urls
