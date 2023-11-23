from typing import List
from pynetboxquery.utils.device_dataclass import Device
from pynetboxquery.utils.error_classes import FileTypeNotSupportedError
from pynetboxquery.utils.read_utils.read_csv import ReadCSV
from pynetboxquery.utils.read_utils.read_txt import ReadTXT
from pynetboxquery.utils.read_utils.read_xlsx import ReadXLSX


# Disabling this pylint warning as it is not necessary.
# pylint: disable = R0903
class ReadFile:
    """
    This class
    """

    @staticmethod
    def read_file(file_path, **kwargs) -> List[Device]:
        """

        :param file_path:
        :param kwargs:
        :return:
        """
        file_type = file_path.split(".")[-1]
        match file_type:
            case "csv":
                device_list = ReadCSV(file_path).read()
            case "txt":
                device_list = ReadTXT(file_path, **kwargs).read()
            case "xlsx":
                device_list = ReadXLSX(file_path, **kwargs).read()
            case _:
                raise FileTypeNotSupportedError(
                    f"The file type '.{file_type}' is not supported by the method."
                )
        return device_list
