from time import strptime


class Configuration:

    def __init__(self):

        settings_dictionary = {}
        with open("python_client.properties") as configuration_file:
            for line in configuration_file:
                name, value = line.partition("=")[::2]
                settings_dictionary[name.strip()] = value.strip().strip("\n")

        properties = type("Names", (), settings_dictionary)

        self._idencodeBaseUrl = settings_dictionary["idencodeBaseUrl"]

        self.pipeline = {
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
                "expirationdate": ""
            },
            "emailSender": {
                "emailto": "",
                "subject": "Your Tech5 IDencode"
            }
        }

        if (properties.includeFaceTemplate is not None and
           properties.includeFaceTemplate.lower() == "true"):
            self.pipeline["facePipeline"]["performTemplateExtraction"] = True
        elif (properties.includeFaceTemplate is not None and
              properties.includeFaceTemplate.lower() == "false"):
            self.pipeline["facePipeline"]["performTemplateExtraction"] = False
        else:
            raise Exception("Configuration property \"includeFaceTemplate\" " +
                            "is missing a required value")

        if (properties.includeCompressedImage is not None and
           properties.includeCompressedImage.lower() == "true"):
            self.pipeline["facePipeline"]["performCompression"] = True
        else:
            self.pipeline["facePipeline"]["performCompression"] = False

        compression_level = self.int_try_parse(properties.compressionLevel)
        if (compression_level is not None and compression_level > 0):
            self.pipeline["facePipeline"]["compressionLevel"] = \
                compression_level

        cols = self.int_try_parse(properties.cols)
        if (cols is not None and cols > 0):
            self.pipeline["barcodeGenerationParameters"]["blockCols"] = cols

        rows = self.int_try_parse(properties.rows)
        if (rows is not None and rows > 0):
            self.pipeline["barcodeGenerationParameters"]["blockRows"] = rows

        error_correction = self.int_try_parse(properties.errorCorrection)
        if (error_correction is not None and error_correction > 0):
            self.pipeline["barcodeGenerationParameters"]["errorCorrection"] = \
                error_correction

        grid_size = self.int_try_parse(properties.gridSize)
        if (grid_size is not None and grid_size > 0):
            self.pipeline["barcodeGenerationParameters"]["gridSize"] = \
                grid_size

        thickness = self.int_try_parse(properties.thickness)
        if (thickness is not None and thickness > 0):
            self.pipeline["barcodeGenerationParameters"]["thickness"] = \
                thickness

        expiry_date = strptime(properties.expiryDate, "%d-%m-%Y")
        if (expiry_date is not None):
            self.pipeline["barcodeGenerationParameters"]["expiryDate"] = \
                str(expiry_date.tm_mday) + "-" + \
                str(expiry_date.tm_mon) + "-" + \
                str(expiry_date.tm_year) + "T23:59:59Z"

        if (properties.email is not None and
           len(properties.email) > 0):
            self.pipeline["emailSender"]["emailto"] = \
             properties.email
        else:
            raise Exception("Configuration property \"email\" is missing " +
                            "a required value")

    def int_try_parse(self, input, base=10, value=None):
        try:
            return int(input, base)
        except ValueError:
            return value
