import logging
from django.conf import settings
from . import models
from django.contrib.auth.models import User
from nio import AsyncClient, LoginResponse
from nio.crypto import OlmDevice

logger = logging.getLogger(__name__)
client = AsyncClient(settings.MATRIX_HOME_SERVER, settings.MATRIX_USERNAME, store_path=settings.STORAGE)

async def send_message(user: User, message: str):
    client.olm = OlmDevice(client)

    # if not os.path.exists(CACHE_FILE):
    #     await client.olm.verify_device()
    #     await client.olm.save_state()

    response = await client.login(settings.MATRIX_PASSWORD)

    if not isinstance(response, LoginResponse):
        logger.info("Failed to login on Matrix:", response)

    matrix_user, _ = models.MatrixInfo.objects.get_or_create(user=user)
    
    if not matrix_user.room_id:
        recipient = f"@{user.username}:{settings.MATRIX_DOMAIN}"
        room_response = await client.room_create(
            is_direct=True,
            invite=[recipient],
            preset="trusted_private_chat"
        )

        matrix_user.room_id = room_response.room_id
        matrix_user.save()

    await client.room_send(
        room_id=room_response.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": message
        }
    )