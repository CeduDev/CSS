import os
import io  # To read from saved file
from google.cloud import storage, vision
import functions_framework

# Add any imports that you may need, but make sure to update requirements.txt


@functions_framework.cloud_event
def image_to_text_storage(cloud_event):
    data = cloud_event.data

    bucket_name = data["bucket"]
    name = data["name"]

    if not (str(name).endswith(".txt")):
        destination_tmp = f"/tmp/{name}"

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(name)
        blob.download_to_filename(destination_tmp)

        client = vision.ImageAnnotatorClient()
        with io.open(destination_tmp, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            detected_text = texts[0].description
        else:
            detected_text = "No text detected"

        output_file_name = str(name).split(".")[0]
        txt_blob_name = f"{output_file_name}.txt"
        txt_blob = bucket.blob(txt_blob_name)
        txt_blob.upload_from_string(detected_text)

    return "Function executed successfully"
