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
    pass