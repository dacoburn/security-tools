import requests
import io


class Sumologic:
    def __init__(self, http_source_url: str):
        """
        Initializes the Sumo Logic client with credentials and HTTP source URL.

        :param access_id: The Sumo Logic Access ID
        :param access_key: The Sumo Logic Access Key
        :param http_source_url: The Sumo Logic HTTP source URL
        """
        self.http_source_url = http_source_url

    def send_events(self, events: list, plugin_name: str) -> dict:
        """
        Will iterate through events and send to SIEM
        :param events: A list containing the events to send:
        :param plugin_name: A string of the plugin name to use for the file name
        :return: A list of errors, if there are no errors the list size will be 0:
        """
        event_file = io.StringIO()
        for event in events:
            # Format timestamp in the required structure
            # timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3] + " +0000"
            #
            # # Format event line
            # event_line = f"{timestamp} INFO [socket-security-tools] {json.dumps(event)}\n"
            # event_file.write(event_line)
            event_file.write(event)

        # Reset the cursor of the file-like object to the start
        event_file.seek(0)
        file_name = f"{plugin_name}.log"
        files = {
            file_name: (file_name, event_file)
        }
        return self.send_event(files)

    def send_event(self, event_data: dict) -> dict:
        """
        Sends an event to the Sumo Logic HTTP source.

        :param event_data: A dictionary containing the event data
        :return: A dictionary with the response status and content
        """
        # headers = {
        #     "Content-Type": "application/json",
        #     # "Authorization": self.auth_header,
        # }

        try:
            response = requests.post(
                self.http_source_url,
                # headers=headers,
                files=event_data
            )
            if response.status_code == 200:
                return {"status": "success", "message": "Event sent successfully."}
            else:
                return {
                    "status": "error",
                    "message": f"Failed to send event. Status code: {response.status_code}",
                    "response": response.text
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
