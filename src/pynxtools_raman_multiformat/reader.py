# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""An example reader implementation based on the MultiFormatReader."""

import logging
from typing import Dict, Any
import h5py
import numpy as np

from pynxtools.dataconverter.readers.multi.reader import MultiFormatReader
from pynxtools.dataconverter.readers.utils import parse_yml

logger = logging.getLogger("pynxtools")

CONVERT_DICT = {}
#    "unit": "@units",
#    "version": "@version",
#    "user": "USER[user]",
#    "instrument": "INSTRUMENT[instrument]",
#    "detector": "DETECTOR[detector]",
#    "sample": "SAMPLE[sample]",
#}


class RamanReaderMulti(MultiFormatReader):
    """MyDataReader implementation for the DataConverter to convert mydata to NeXus."""

    supported_nxdls = ["NXraman"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.extensions = {
            ".yml": self.handle_eln_file,
            ".yaml": self.handle_eln_file,
            ".txt": self.handle_txt_file}
         #   ".json": self.set_config_file,
        #}

        self.txt_line_skips = None

    def set_config_file(self, file_path: str) -> Dict[str, Any]:
        if self.config_file is not None:
            logger.info(
                f"Config file already set. Replaced by the new file {file_path}."
            )
        self.config_file = file_path
        return {}



    def handle_eln_file(self, file_path: str) -> Dict[str, Any]:
        self.eln_data = parse_yml(
            file_path,
            convert_dict=CONVERT_DICT,
            parent_key="/ENTRY[entry]",
        )
        #self.txt_line_skips = self.eln_data.get('/ENTRY[entry]/skip')

        return {}

    def handle_txt_file(self, filepath) -> Dict[str, Any]:
        self.read_txt_file(filepath)
        return {}









    def get_attr(self, key: str, path: str) -> Any:
        """
        Get the metadata that was stored in the main file.
        """
        # This uses the path given from the config file (path = the part after "@attrs:")
        # to get the corresponting value stored at in the eln_data.yaml file, at the 
        # path value.
        return self.eln_data.get(path)

    def read_txt_file(self, filepath):
        with open(filepath, "r") as file:
            lines = file.readlines()

        # Initialize dictionaries to hold header and data sections
        header_dict = {}
        data = []
        line_count = 0
        header_length = None

        # Track current section
        current_section = None



        for line in lines:
            line_count += 1
            line = line.strip()  # Remove any leading/trailing whitespace
            if line.startswith("[Header]"):
                current_section = "header"
                continue
            elif line.startswith("[Data]"):
                header_length = line_count + 2
                current_section = "data"

                continue

            # Parse the header section
            if current_section == "header" and "=" in line:
                key, value = line.split("=", 1)
                header_dict[key.strip()] = value.strip()

            # Parse the data section
            elif current_section == "data" and "," in line:
                if line_count <= header_length:
                    if line.startswith("[Header]"):
                        print("We have to do something here")
                if line_count > header_length:
                    values = line.split(",")
                    data.append([float(values[0].strip()), float(values[1].strip())])

        #transform linewise read data to colum style data



        # Transform: [[A, B], [C, D], [E, F]] into [[A, C, E], [B, D, F]]
        data = [list(item) for item in zip(*data)]

        data = np.transpose(data)

        data_dict = {
            "data/x_values": data[:, 0],
            "data/y_values": data[:, 1]
        }

        self.txt_data = data_dict
        self.txt_header = header_dict


    def read_txt_columns(self, filepath):
        data = np.loadtxt(filepath, delimiter=',')

        # Convert the array into a dictionary with labeled columns
        data_dict = {
            "data/x_values": data[:, 0],
            "data/y_values": data[:, 1]
        }

        A=self.transform_nm_to_wavenumber(532.1,data_dict["data/x_values"])
        print(A,"A")
        return data_dict

    def get_eln_data(self, key: str, path: str) -> Any:
        """Returns data from the given eln path."""
        if self.eln_data is None:
            return None
        upper_and_lower_mixed_nexus_concepts = ["/detector_TYPE[",
                                        "/beam_TYPE[",
                                        "/source_TYPE[",
                                        "/polfilter_TYPE[",
                                        "/spectral_filter_TYPE[",
                                        "/temp_control_TYPE[",
                                        "/software_TYPE[",
                                        "/LENS_OPT["

        ]
        if self.eln_data.get(key) is None:
            for string in upper_and_lower_mixed_nexus_concepts:
                key = key.replace(string,"/[")
            # add only characters, if they are lower case and if they are not "[" or "]"
            result = ''.join([char for char in key if not (char.isupper() or char in '[]')])
            result = result.replace("entry","ENTRY[entry]") # CHANGE THIS LATER
            if self.eln_data.get(result) is not None:
                return self.eln_data.get(result)
            else:
                return "Parsing error?"
        return self.eln_data.get(key)

    def get_data(self, key: str, path: str) -> Any:
        """Returns measurement data from the given eln_data entry."""
        if path.endswith(("x_values", "y_values","x_values_raman")):
            return self.txt_data.get(f"data/{path}")
        else:
            logger.warning(f"No axis name corresponding to the path {path}.")


    def post_process(self) -> None:
        """
        Do postprocessing after all files and config file are read.
        """

        def transform_nm_to_wavenumber(self, lambda_laser, lambda_measurement):
            stokes_raman_shift = -(1e7 / lambda_measurement - 1e7 / lambda_laser)
            return stokes_raman_shift

        def get_incident_wavelength_from_NXraman(self):
            substring = "/beam_incident/wavelength"

            # Find matching keys with contain this substring
            wavelength_keys = [key for key in self.eln_data if substring in key]
            # Filter the matching keys for the strings, which contain this substring at the end only
            filtered_list = [string for string in wavelength_keys if string.endswith(substring)]
            # get the laser wavelength
            laser_wavelength = self.eln_data.get(filtered_list[0])
            return laser_wavelength

        laser_wavelength = get_incident_wavelength_from_NXraman(self)
        x_values_raman = transform_nm_to_wavenumber(self, laser_wavelength, self.txt_data["data/x_values"])

        self.txt_data["data/x_values_raman"] = x_values_raman




READER = RamanReaderMulti

# Use this command in this .py file folder:
# dataconverter eln_data.yaml Si-wafer-Raman-Spectrum-1.txt  -c config_file.json --reader raman_multi --nxdl NXraman --output output_raman.nxs
#
# Remaining Warnings
# Could not find value for key /ENTRY[entry]/DATA[data]/x_values_raman/@long_name with value @attrs:/ENTRY[entry]/data/longname_x_raman.
# Tried prefixes: [('@attrs', '/ENTRY[entry]/data/longname_x_raman')].
# WARNING: Missing attribute: "/ENTRY[entry]/definition/@URL"
# WARNING: Field /ENTRY[entry]/DATA[data]/y_values/@unit written without documentation.
# WARNING: Field /ENTRY[entry]/DATA[data]/x_values/@unit written without documentation.
# WARNING: Field /ENTRY[entry]/DATA[data]/x_values_raman/@unit written without documentation.