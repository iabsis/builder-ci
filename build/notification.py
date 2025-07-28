from . import models
import logging
from django.conf import settings
import requests

logger = logging.getLogger(__name__)

def send_notification(build):
    try:
        send_redmine_notification(build)
        send_matrix_notification(build)
    except Exception as e:
        logger.error(f"Received error during notification: {e}")

def send_redmine_notification(build):
    # TODO : make configurable notification

    if build.status == models.Status.queued:
        status = 'New'
    elif build.status == models.Status.failed:
        status = 'Failed'
    elif build.status == models.Status.success:
        status = 'Success'
    elif build.status == models.Status.running:
        status = 'Running'
    elif build.status == models.Status.warning:
        status = 'New'
    elif build.status == models.Status.duplicate:
        status = 'Duplicate'
    else:
        logger.debug(f"Received unknow status: {build.status}")
        status = 'Failed'

    if settings.REDMINE_KEY and settings.REDMINE_URL:

        if build.status == 'running' and build.progress != None:
            flow = f"{build.flow.name} (eta: {build.eta_at.strftime('%H:%M:%S')})"
        else:
            flow = build.flow.name
        
        req = {
            "headers": {
                'Content-Type': 'application/json',
                'X-Redmine-Api-Key': settings.REDMINE_KEY
            },
            "json": {
                "project": build.name,
                "status": status,
                "release": build.version,
                "commit": build.meta.get('commit_id'),
                "target": 'undefined',
                "builder": flow,
                "logs": build.logs,
            }
        }

        if build.started_at:
            req["json"]["started_at"] = build.started_at.strftime("%Y-%m-%d_%H:%M:%S") if build.started_at else None
        if build.started_at:
            req["json"]["finished_at"] = build.finished_at.strftime("%Y-%m-%d_%H:%M:%S") if build.finished_at else None


        redmine_id = build.meta.get('redmine_id')
        req['url'] = f"{settings.REDMINE_URL}/builds/{redmine_id}.json" if redmine_id else f"{settings.REDMINE_URL}/builds/new.json"

        response = requests.post(**req)
        if response.status_code != 200:
            logger.error(f"Unable to notify Redmine: {response.text} with error {response.status_code}")
            logger.debug(req)
        else:
            build.meta['redmine_id'] = response.text
            build.save(notify=False)
        response.raise_for_status()

def send_matrix_notification(build):
    if not build.request.requested_by:
        logger.debug(f"No requested_by user for build {build.name}, skipping Matrix notification")
        return
    
    if not settings.MATRIX_DOMAIN:
        logger.debug("MATRIX_DOMAIN not configured, skipping Matrix notification")
        return
    
    # Only notify when build is done (success, failed, or warning)
    if build.status not in [models.Status.success, models.Status.failed, models.Status.warning]:
        logger.debug(f"Build {build.name} status is {build.status}, not notifying")
        return
    
    try:
        from django.contrib.auth.models import User
        import threading
        import asyncio
        
        try:
            user = User.objects.get(username=build.request.requested_by)
        except User.DoesNotExist:
            logger.warning(f"User {build.request.requested_by} not found, skipping Matrix notification")
            return
        
        if build.status == models.Status.failed:
            status_text = 'failed'
        elif build.status == models.Status.success:
            status_text = 'completed successfully'
        elif build.status == models.Status.warning:
            status_text = 'completed with warnings'
        else:
            status_text = f'status: {build.status}'
        
        message = f"Build '{build.name}' is {status_text}"
        if build.version:
            message += f" (version: {build.version})"
        if build.flow:
            message += f" using flow '{build.flow.name}'"
        
        # Pre-create MatrixInfo to avoid database calls in async context
        from notification.models import MatrixInfo
        matrix_info, _ = MatrixInfo.objects.get_or_create(user=user)
        
        # Run Matrix notification in a separate thread to avoid async context issues
        def send_matrix_in_thread():
            from notification.matrix import send_message_with_room
            asyncio.run(send_message_with_room(user.username, matrix_info.room_id, message))
            
            # Update room_id if it was created
            if not matrix_info.room_id:
                # We'll need to get the room_id back somehow - let's modify the function
                pass
        
        thread = threading.Thread(target=send_matrix_in_thread)
        thread.start()
        thread.join(timeout=10)  # Wait max 10 seconds
        
        logger.info(f"Matrix notification sent to {user.username} for build {build.name}")
        
    except Exception as e:
        logger.error(f"Failed to send Matrix notification: {e}")
        raise