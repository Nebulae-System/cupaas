from app.kafka import pipe
from app.config import KAFKA_TOPIC_GITHUB_EVENT, KAFKA_TOPIC_GIT_CLONE


@pipe(KAFKA_TOPIC_GITHUB_EVENT, KAFKA_TOPIC_GIT_CLONE)
async def github_events(data, context):
    mongo = context["mongo"]
    body = data["body"]
    project = mongo.get_collection("project").find_one({
        "name": body["repository"]["full_name"],
        "git_source": "github",
        "ref": body["ref"]
    })
    if not project:
        return
    url = body["repository"]["url"]
    ref = project["ref"]
    zip_url = f"{url}/archive/{ref}.zip"
    mongo.get_collection("deploy").insert_one({
        "project_id": project["_id"],
        "data": data,
    })
    project["_id"] = str(project["_id"])
    return {
        "project": project,
        "zip_url": zip_url,
    }
