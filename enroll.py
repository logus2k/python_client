import os
import json
import base64

# pip install requests-toolbelt
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests


def get_pipeline():

    configuration_settings = {}
    with open("python_client.properties") as configuration_file:
        for line in configuration_file:
            name, value = line.partition("=")[::2]
            configuration_settings[name.strip()] = value.strip().strip("\n")

    settings = ()
    names = type("Names", settings, configuration_settings)

    email = names.email  # type: ignore

    pipeline = {
        "facePipeline": {
            "performTemplateExtraction": True,
            "faceDetectorConfidence": 0.6,
            "faceSelectorAlg": 1,
            "performCompression": True,
            "compressionLevel": 1
        },
        "barcodeGenerationParameters": {
            "blockCols": 30,
            "blockRows": 8,
            "errorCorrection": 12,
            "gridSize": 7,
            "thickness": 2,
            "expirationdate": "2023-12-03T23:59:59Z"
        },
        "emailSender": {
            "emailto": email,
            "subject": "Your Tech5 IDencode"
        }
    }

    return pipeline


pipeline = get_pipeline()

multipart_data = MultipartEncoder(
    fields={"face_image": ("antonio.jpg", open("antonio.jpg", "rb"),
                           "image/jpeg"),
            "demog": ("demog.txt", open("demog.txt", "rb"),
                      "application/octet-stream"),
            "pipeline": ("pipeline.json", json.dumps(pipeline),
                         "application/json")
            }
        )


# Dump the request
# m.to_string()

response = requests.post(
    "https://idencode.tech5-sa.com/v1/enroll",
    data=multipart_data,  # type: ignore
    headers={"Content-Type": multipart_data.content_type})

json_attributes = json.loads(response.text)
uuid = json_attributes["uuid"]
base64_image = json_attributes["image"]

output_directory = os.path.join(os.getcwd(), "output", uuid)
os.makedirs(output_directory, exist_ok=True)

file = open(os.path.join(output_directory, "pipeline.json"), "w")
file.write(json.dumps(pipeline))
file.close()

file = open(os.path.join(output_directory, "response.json"), "w")
file.write(response.text)
file.close()

file = open(os.path.join(output_directory, "cryptograph.jpg"), "wb")
file.write(base64.b64decode(base64_image))
file.close()
