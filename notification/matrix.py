import logging
from django.conf import settings
from . import models
from django.contrib.auth.models import User
from nio import AsyncClient, LoginResponse

logger = logging.getLogger(__name__)

async def send_message(user: User, message: str):
    logger.info(f"Attempting to send Matrix message to user: {user.username}")
    logger.info(f"Matrix config - Server: {settings.MATRIX_HOME_SERVER}, Username: {settings.MATRIX_USERNAME}, Domain: {settings.MATRIX_DOMAIN}")
    
    # Create client instance for this session
    logger.info(f"Using Matrix server: {settings.MATRIX_HOME_SERVER}")
    client = AsyncClient(settings.MATRIX_HOME_SERVER, settings.MATRIX_USERNAME, store_path=settings.STORAGE)
    
    try:
        logger.info("Setting Matrix access token...")
        # Use access token instead of password login
        client.access_token = settings.MATRIX_TOKEN
        
        if not settings.MATRIX_TOKEN:
            logger.error("MATRIX_TOKEN not configured")
            return
            
        logger.info("Matrix client configured with access token")
            
        matrix_user, _ = models.MatrixInfo.objects.get_or_create(user=user)
        logger.info(f"MatrixInfo for {user.username}: room_id={matrix_user.room_id}")
        
        if not matrix_user.room_id:
            recipient = f"@{user.username}:{settings.MATRIX_DOMAIN}"
            logger.info(f"Creating Matrix room for recipient: {recipient}")
            
            room_response = await client.room_create(
                is_direct=True,
                invite=[recipient]
            )

            if hasattr(room_response, 'room_id'):
                matrix_user.room_id = room_response.room_id
                matrix_user.save()
                logger.info(f"Created room {room_response.room_id} for {user.username}")
            else:
                logger.error(f"Failed to create room: {room_response}")
                return

        logger.info(f"Sending message to room {matrix_user.room_id}: {message}")
        
        send_response = await client.room_send(
            room_id=matrix_user.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message
            }
        )
        
        if hasattr(send_response, 'event_id'):
            logger.info(f"Message sent successfully, event_id: {send_response.event_id}")
        else:
            logger.error(f"Failed to send message: {send_response}")
    
    except Exception as e:
        logger.error(f"Matrix operation failed: {e}")
    finally:
        await client.close()

async def send_message_with_room(username: str, room_id: str, message: str):
    logger.info(f"Sending Matrix message to {username}, room_id: {room_id}")
    
    # Create client instance for this session
    client = AsyncClient(settings.MATRIX_HOME_SERVER, settings.MATRIX_USERNAME, store_path=settings.STORAGE)
    
    try:
        logger.info("Setting Matrix access token...")
        # Use access token instead of password login
        client.access_token = settings.MATRIX_TOKEN
        
        if not settings.MATRIX_TOKEN:
            logger.error("MATRIX_TOKEN not configured")
            return
            
        logger.info("Matrix client configured with access token")

        # If no room_id, create one
        if not room_id:
            recipient = f"@{username}:{settings.MATRIX_DOMAIN}"
            logger.info(f"Creating Matrix room for recipient: {recipient}")
            
            try:
                room_response = await client.room_create(
                    is_direct=True,
                    invite=[recipient]
                )
                logger.info(f"Room creation response: {room_response}")
                logger.info(f"Room response type: {type(room_response)}")
                
                if hasattr(room_response, 'room_id'):
                    room_id = room_response.room_id
                    logger.info(f"Created room {room_id} for {username}")
                else:
                    logger.error(f"Failed to create room: {room_response}")
                    return
            except Exception as e:
                logger.error(f"Exception during room creation: {e}")
                return

        logger.info(f"Sending message to room {room_id}: {message}")
        
        try:
            send_response = await client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message
                }
            )
            logger.info(f"Send response: {send_response}")
            logger.info(f"Send response type: {type(send_response)}")
            
            if hasattr(send_response, 'event_id'):
                logger.info(f"Message sent successfully, event_id: {send_response.event_id}")
            else:
                logger.error(f"Failed to send message: {send_response}")
        except Exception as e:
            logger.error(f"Exception during message send: {e}")
            return
    
    except Exception as e:
        logger.error(f"Matrix operation failed: {e}")
    finally:
        await client.close()

async def send_message_with_room_update(username: str, room_id: str, message: str):
    """Send Matrix message and return the room_id (existing or newly created)"""
    logger.info(f"Sending Matrix message to {username}, room_id: {room_id}")
    
    # Create client instance for this session
    client = AsyncClient(settings.MATRIX_HOME_SERVER, settings.MATRIX_USERNAME, store_path=settings.STORAGE)
    
    try:
        logger.info("Setting Matrix access token...")
        client.access_token = settings.MATRIX_TOKEN
        
        if not settings.MATRIX_TOKEN:
            logger.error("MATRIX_TOKEN not configured")
            return None
            
        logger.info("Matrix client configured with access token")

        # If no room_id, create one
        if not room_id:
            recipient = f"@{username}:{settings.MATRIX_DOMAIN}"
            logger.info(f"Creating Matrix room for recipient: {recipient}")
            
            try:
                room_response = await client.room_create(
                    is_direct=True,
                    invite=[recipient]
                )
                
                if hasattr(room_response, 'room_id'):
                    room_id = room_response.room_id
                    logger.info(f"Created room {room_id} for {username}")
                else:
                    logger.error(f"Failed to create room: {room_response}")
                    return None
            except Exception as e:
                logger.error(f"Exception during room creation: {e}")
                return None

        logger.info(f"Sending message to room {room_id}: {message}")
        
        try:
            send_response = await client.room_send(
                room_id=room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message
                }
            )
            
            if hasattr(send_response, 'event_id'):
                logger.info(f"Message sent successfully, event_id: {send_response.event_id}")
                return room_id  # Return the room_id for database update
            else:
                logger.error(f"Failed to send message: {send_response}")
                return None
        except Exception as e:
            logger.error(f"Exception during message send: {e}")
            return None
    
    except Exception as e:
        logger.error(f"Matrix operation failed: {e}")
        return None
    finally:
        await client.close()

async def send_message_direct(username: str, room_id: str, message: str):
    # Create client instance for this session
    # Use Matrix username as-is (should be @username:domain format)
    client = AsyncClient(settings.MATRIX_HOME_SERVER, settings.MATRIX_USERNAME, store_path=settings.STORAGE)
    
    try:
        logger.info("Setting Matrix access token...")
        # Use access token instead of password login
        client.access_token = settings.MATRIX_TOKEN
        
        if not settings.MATRIX_TOKEN:
            logger.error("MATRIX_TOKEN not configured")
            return
            
        logger.info("Matrix client configured with access token")

        # If no room_id, create one
        if not room_id:
            recipient = f"@{username}:{settings.MATRIX_DOMAIN}"
            room_response = await client.room_create(
                is_direct=True,
                invite=[recipient]
            )
            
            if hasattr(room_response, 'room_id'):
                room_id = room_response.room_id
                logger.info(f"Created room {room_id} for {username}")
            else:
                logger.error(f"Failed to create room: {room_response}")
                return

        await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message
            }
        )
    
    except Exception as e:
        logger.error(f"Matrix operation failed: {e}")
    finally:
        await client.close()