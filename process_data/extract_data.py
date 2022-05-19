#!/usr/bin/env python3
import enum
import sys


class Fields(enum.Enum):
    RecordType = 3
    TimeStamp = 2
    GlucosePuntual = 5
    GlucosePeriodic = 4


class RecordTypeOutput(enum.Enum):
    Puntual = "puntual"
    Periodic = "periodic"


class RecordType(enum.Enum):
    Puntual = "1"
    Periodic = "0"


class ExportFileFields(enum.Enum):
    Type = "type"
    Timestamp = "timestamp"
    GlucoseValue = "glucose_value"


def get_header():
    ret = f"{ExportFileFields.Type.value}\t{ExportFileFields.Timestamp.value}\t{ExportFileFields.GlucoseValue.value}"
    return ret


def process_file(_filename, _outfile=""):

    fs = open(_filename)
    if _outfile == "":
        fd = sys.stdout
    else:
        fd = open(_outfile)

    fd.write(f"{get_header()}\n")

    for line in fs.readlines():
        type = ""
        fields = line.split(",")
        glucose_value = 0
        if fields[Fields.RecordType.value] == RecordType.Puntual.value:
            type = RecordTypeOutput.Puntual.value
            glucose_value = float(fields[Fields.GlucosePuntual.value])
        elif fields[Fields.RecordType.value] == RecordType.Periodic.value:
            type = RecordTypeOutput.Periodic.value
            glucose_value = fields[Fields.GlucosePeriodic.value]

        if type != "":
            timestamp = fields[Fields.TimeStamp.value]
            fd.write(f"{type}\t{timestamp}\t{glucose_value}\n")

    if _outfile != "":
        fd.close()
    fs.close()


def main(_filename, _outfile):
    process_file(_filename, _outfile)


if __name__ == "__main__":
    filename = "datos.csv"
    outfile = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    if len(sys.argv) > 2:
        outfile = sys.argv[2]
    main(filename, outfile)
