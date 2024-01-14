import functions_framework
import google.cloud.secretmanager

import bot_controller


#################################
def run_bot(token: str, request_json):
    data = request_json
    if 'message' in data:
        message = data['message']
        bot_controller.BotController(token).handle_message(message)
        return True
    return False


#####################################################################################

def get_secret(secret_id, project_id="worldwidenewstelegrambot", version_id="latest"):
    # Створіть клієнт менеджера секретів.
    client = google.cloud.secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    # Отримайте значення секрету.
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


####################################################################################
@functions_framework.http
def handle_request(request):
    secret_id = "bot_token"
    secret = get_secret(secret_id)
    request_json = request.get_json(silent=True)
    run_bot(secret, request_json)
    return f'Request: {request}\nRequest proccessing is finished!'
