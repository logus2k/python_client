import os
import json
import base64

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

import pipeline


class EnrollResult:

    def __init__(self, **kwargs):
        self.errorCode = kwargs["errorCode"]
        self.uuid = kwargs["uuid"]


class IDencode:

    def __init__(self):
        self._config = pipeline.Configuration()

    def enroll(self) -> EnrollResult:

        multipartdata_fields = {}

        face_image_file = os.path.basename(self._config._faceImagePath)
        face_image_field = (face_image_file,
                            open(self._config._faceImagePath, "rb"),
                            "image/jpeg")
        multipartdata_fields["face_image"] = face_image_field

        if self._config._includeDemographics is True:
            demographics_file = \
                os.path.basename(self._config._demographicsFilePath)
            demographics_field = (demographics_file,
                                  open(self._config._demographicsFilePath,
                                       "rb"),
                                  "application/octet-stream")
            multipartdata_fields["demog"] = demographics_field

        pipeline_field = ("pipeline.json",
                          json.dumps(self._config.pipeline),
                          "application/json")
        multipartdata_fields["pipeline"] = pipeline_field

        multipart_data = MultipartEncoder(fields=multipartdata_fields)

        response = requests.post(
            self._config._idencodeBaseUrl + "enroll",
            data=multipart_data,
            headers={"Content-Type": multipart_data.content_type})

        json_attributes = json.loads(response.text)
        uuid = json_attributes["uuid"]
        base64_image = json_attributes["image"]

        output_directory = os.path.join(self._config._outputFilesPath, uuid)
        os.makedirs(output_directory, exist_ok=True)

        file = open(os.path.join(output_directory, "pipeline.json"), "w")
        file.write(json.dumps(self._config.pipeline))
        file.close()

        file = open(os.path.join(output_directory, "response.json"), "w")
        file.write(response.text)
        file.close()

        file = open(os.path.join(output_directory, "cryptograph.jpg"), "wb")
        file.write(base64.b64decode(base64_image))
        file.close()

        return EnrollResult(uuid=uuid, errorCode=0)


if __name__ == "__main__":

    enrollResult = IDencode().enroll()

    if (enrollResult.errorCode != 0):
        print("Error code: " + str(enrollResult.errorCode))
    else:
        print(enrollResult.uuid)
