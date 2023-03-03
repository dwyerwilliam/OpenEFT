from datetime import datetime
FS_CHAR = 0x1C # Record
GS_CHAR = 0x1D # Field
RS_CHAR = 0x1E # Subfield 
US_CHAR = 0x1F # Item


def join(iterable, sep=":"):
    return ':'.join([str(x) for x in iterable])


def join_dict(d, sep=GS_CHAR, endsep=FS_CHAR):
    x = bytearray()
    i = 0
    numKeys = len(d.keys())
    for key in d.keys():
        if i < numKeys-1:
            if type(d[key]) == type(bytes()):
                x = x + bytearray(key, 'ascii') + bytes(":", 'ascii') + d[key]
            else:
                x = x + bytearray(key, 'ascii') + bytes(":", 'ascii')
                x = x + bytearray(str(d[key]), 'ascii')
                x = x + bytes(chr(sep), 'ascii')
        else:
            if type(d[key]) == type(bytes()):
                x = x + bytearray(key, 'ascii') + bytes(":",
                                                        'ascii') + d[key] + bytes(chr(endsep), 'ascii')
            else:
                x = x + bytearray(key, 'ascii') + bytes(":", 'ascii') + \
                    bytearray(d[key], 'ascii') + bytes(chr(endsep), 'ascii')
        i += 1
    return x


def get_date():
    # YYYYMMdd
    return datetime.now().strftime("%Y%m%d:%H%M%S")


class Record:
    def __init__(self, rtype="0", idc=0):
        self.rtype = rtype
        self.len = "1"  # Header, first record
        self.idc = idc
        self.full_time = get_date()
        self.dat = self.full_time.split(':')[0]
        self.cnt = []

    def _get_len(self):
        tmp = len(join_dict(self._get_dict()))
        self.len = tmp + len(str(tmp)) - 1
        return self.len

    def _get_dict(self):  # Overrideable if needed
        return {self.rtype + ".001": self.len}

    def repr(self):
        self._get_len()
        return join_dict(self._get_dict())

    def __cnt__(self):
        """Used to return special info for Type1 records."""
        tmp = self.idc
        if tmp >= 0 and tmp < 10:
            tmp = "0" + str(tmp)
        else:
            tmp = str(tmp)
        return self.rtype + chr(US_CHAR) + tmp

    def write_to_file(self, fname):
        with open(fname, 'wb') as f:
            f.write(self.repr())
            for record in self.cnt:
                f.write(record.repr())


class Type1(Record):
    def __init__(self):
        super().__init__()
        self.ver = "0200"
        self.cnt = []
        self.cnt_total = 1  # Pointer to self.cnt
        self.tot = "FAUF"
        self.pry = 6  # Priority (1-10, default: 6)
        self.dai = "WVIAFIS0Z"  # Destination, CJIS
        self.ori = "WVATF0900"  # Source, ATF
        self.tcn = self.ori + '-' + self.full_time + "-EFTC-"
        self.nsr = "00.00"  # Only for type 4, we use type 14
        self.ntr = "00.00"  # Only for type 4
        self.record_string = ""

    def get_len(self):
        tmp = 0
        for record in self.cnt:
            tmp += record._get_len()
        tmp += self._get_len()
        self.len = tmp

    def get_count_string(self):
        x = "1"+chr(US_CHAR)+str(len(self.cnt))
        if len(self.cnt) > 0:
            x = x + chr(RS_CHAR) + '_'.join([str(x.__cnt__())
                                             for x in self.cnt]).replace('_', chr(RS_CHAR))
        return x

    def add_record(self, record):
        self.cnt.append(record)

    def _get_dict(self):
        return {
            "1.001": self.len,
            "1.002": self.ver,
            "1.003": self.get_count_string(),
            "1.004": self.tot,
            "1.005": self.dat,
            "1.006": self.pry,
            "1.007": self.dai,
            "1.008": self.ori,
            "1.009": self.tcn,
            "1.011": self.nsr,
            "1.012": self.ntr
        }


class Type2(Record):
    def __init__(self, idc=0):
        super().__init__("2", idc)
        self.ak = ""
        self.pob = ""
        self.dob = ""
        self.agr = "1899"
        self.race = ""
        self.eye = ""
        self.hair = ""
        self.rsn = ""
        self.dfp = ""
        self.name = ""
        self.residence = ""
        self.birth = ""
        self.height = ""
        self.weight = ""
        self.ice = ""
        self.acn = ""
        self.amp = ""

    def get_user_input(self):
        fname = input("First Name: ")
        mname = input("Middle Name: ")
        lname = input("Last Name: ")
        self.ak = input("Aliases (comma separated): ")
        stateCurrent = input("Current State 2-Letter Code (e.g. AZ, NY): ")
        stateBorn = input("Start Born 2-Letter Code (e.g. AZ, NY): ")
        ssn = input("Social Security Number (no dashes): ")
        addr = input("Address: ")
        self.dob = input("Date of birth (YYYmmdd): ")
        self.race = input("Race (A=Asian, B=Black, I=American Indian, W=White or Latino): ")
        eye = input("Eye Color (BLK,BLU,BRO,GRY,GRN,HAZ,MAR,MUL,PINK): ")
        hair = input(
            "Hair Color: (BAL,BLK,BLN,BLU,BRO,GRY,GRN,ONG,PNK,PLE,RED,SDY,WHI)")
        self.height = input("Height (inches): ")
        self.weight = input("Weight (lbs): ")
        self.rsn = input("Reason (default: Firearms): ")
        if len(self.rsn) < 1:
            self.rsn = "Firearms"
        self.sex = input("Sex (M=Male, F=Female): ")
        self.amp = input("Missing Fingers (csv, 1-10): ") # Need to fix this


    def _get_dict(self):
        return {
            "2.001": self.len,
            "2.002": self.idc,
            "2.005": "N",
            "2.018": self.name,
            "2.019": self.ak,
            "2.020": self.pob,
            "2.022": self.dob,
            "2.023": self.agr,
            "2.025": self.race,
            "2.031": self.eye,
            "2.037": self.rsn,
            "2.038": self.dfp,
            "2.067": self.ice,
            "2.071": self.acn,
            "2.084": self.amp,
            "2.8031": self.residence,
            "2.8033": self.birth,
            "2.8035": self.height,
            "2.8036": self.weight,
        }


class Type14(Record):
    def __init__(self, idc=0):
        super().__init__("14", idc)
        self.isc = "1"  # Default for fingrpint card
        self.scu = "1"  # Pixels per inch = 1, pixels per cm = 2
        self.imp = "1"  # Impression type, default=1 (rolled)
        self.src = ""  # Source agency
        self.fcd = ""  # Fingerprint capture date
        self.hll = ""  # Horizontal line length
        self.vll = ""  # Vertical line length
        self.slc = ""  # Scale units
        self.thps = ""  # Transmitted horizontal pixel scale
        self.tvps = ""  # Transmitted verical pixel scale
        self.cga = "WSQ20"  # Compression algorithm (default WSQ20)
        self.bpx = "8"  # Bits per pixel
        self.ppd = ""  # Print position descriptors
        self.file = ""
        self.score = ""
        self.fgp = "0"  # 1-15 and 19
        # four finger slap = 13 and 14
        # Individual thumb = 11 and 12
        self.dat=""

    def build(self):
        self.get_finger_position()
        self.dat = self.read_data()

    def read_data(self):
        x = b''
        with open(self.file, 'rb') as f:
            x = f.read()
        return x

    def get_finger_position(self):
        f = self.file.split('/')[-1]
        if 'R_' in f:
            # Right
            if "THUMB2" in f:
                return "11"
            elif "THUMB" in f:
                return "1"
            elif "INDEX" in f:
                return "2"
            elif "MIDDLE" in f:
                return "3"
            elif "RING" in f:
                return "4"
            elif "LITTLE" in f:
                return "5"
        elif 'L_' in f:
            # left
            if "THUMB2" in f:
                return "12"
            elif "THUMB" in f:
                return "6"
            elif "INDEX" in f:
                return "7"
            elif "MIDDLE" in f:
                return "8"
            elif "RING" in f:
                return "9"
            elif "LITTLE" in f:
                return "10"
        else:
            return "0"


    def _get_dict(self):
        return {
            "14.001": self.len,
            "14.002": self.idc,
            "14.003": self.imp,
            "14.004": self.src,
            "14.005": self.fcd,
            "14.006": self.hll,
            "14.007": self.vll,
            "14.008": self.scu,
            "14.009": self.thps,
            "14.010": self.tvps,
            "14.011": self.cga,
            "14.012": self.bpx,
            "14.013": self.fgp,
            "14.014": self.ppd,
#            "14.022": self.fgp + RS_CHAR + self.score # Disable until verify
            "14.200": self.isc,
            "14.999": self.dat
        }


class EFT:
    def __init__(self, fname, ask_q=True):
        self.fname = fname
        self.record = Type1()
        if ask_q:
            x = Type2()
            x.get_user_input()
            self.record.add_record(x)

    def gen_fingerprints(self):

        self.record.write_to_file(self.fname + '.eft')
        pass


if __name__ in '__main__':
    print("FS: ", chr(FS_CHAR), "GS: ", chr(GS_CHAR),
          "RS: ", chr(RS_CHAR), "US: ", chr(US_CHAR))
    print(get_date())
    x = Type1()
    y = Type2()
    x.add_record(y)
    z = Type14()
    x.add_record(z)
    x.write_to_file('Desktop/OpenEFT/build/bin/test.eft')
