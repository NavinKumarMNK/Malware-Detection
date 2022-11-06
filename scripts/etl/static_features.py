import itertools
import pefile
import math
import hashlib
from collections import OrderedDict


def get_entropy(data):
    if not data:
        return 0

    entropy = 0
    for x in range(256):
        p_x = float(data.count(chr(x)))/len(data)
        if p_x > 0:
            entropy += - p_x*math.log(p_x, 2)
    return entropy


class StaticFeatures:

    def __init__(self, base_path, filepath, filename):
        self.base_path = base_path
        self.filepath = filepath
        self.filename = filename

    def EXTRACT_OPTIONAL_HEADER_INFO(self, LResource, Resources_header, file_path, fileName):

        pefile_info = pefile.PE(file_path)

        LResource[Resources_header['Name']] = fileName
        LResource[Resources_header['MajorLinkerVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MajorLinkerVersion
        LResource[Resources_header['MinorLinkerVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MinorLinkerVersion
        LResource[Resources_header['SizeOfCode']
                  ] = pefile_info.OPTIONAL_HEADER.SizeOfCode
        LResource[Resources_header['SizeOfInitializedData']
                  ] = pefile_info.OPTIONAL_HEADER.SizeOfInitializedData
        LResource[Resources_header['SizeOfUninitializedData']
                  ] = pefile_info.OPTIONAL_HEADER.SizeOfUninitializedData

        try:
            LResource[Resources_header['AddressOfEntryPoint']
                      ] = pefile_info.OPTIONAL_HEADER.AddressOfEntryPoint
            LResource[Resources_header['BaseOfCode']
                      ] = pefile_info.OPTIONAL_HEADER.BaseOfCode
            LResource[Resources_header['ImageBase']
                      ] = pefile_info.OPTIONAL_HEADER.ImageBase
        except:
            LResource[Resources_header['AddressOfEntryPoint']] = 0
            LResource[Resources_header['BaseOfCode']] = 0
            LResource[Resources_header['ImageBase']] = 0

        LResource[Resources_header['SectionAlignment']
                  ] = pefile_info.OPTIONAL_HEADER.SectionAlignment
        LResource[Resources_header['FileAlignment']
                  ] = pefile_info.OPTIONAL_HEADER.FileAlignment
        LResource[Resources_header['MajorOperatingSystemVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MajorOperatingSystemVersion
        LResource[Resources_header['MinorOperatingSystemVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MinorOperatingSystemVersion
        LResource[Resources_header['MajorImageVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MajorImageVersion
        LResource[Resources_header['MinorImageVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MinorImageVersion
        LResource[Resources_header['MajorSubsystemVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MajorSubsystemVersion
        LResource[Resources_header['MinorSubsystemVersion']
                  ] = pefile_info.OPTIONAL_HEADER.MinorSubsystemVersion
        LResource[Resources_header['SizeOfImage']
                  ] = pefile_info.OPTIONAL_HEADER.SizeOfImage
        LResource[Resources_header['SizeOfHeaders']
                  ] = pefile_info.OPTIONAL_HEADER.SizeOfHeaders

        LResource[Resources_header['Subsystem']
                  ] = pefile_info.OPTIONAL_HEADER.Subsystem
        LResource[Resources_header['DllCharacteristics']
                  ] = pefile_info.OPTIONAL_HEADER.DllCharacteristics
        try:
            LResource[Resources_header['SizeOfStackReserve']
                      ] = pefile_info.OPTIONAL_HEADER.SizeOfStackReserve
            LResource[Resources_header['SizeOfStackCommit']
                      ] = pefile_info.OPTIONAL_HEADER.SizeOfStackCommit
            LResource[Resources_header['SizeOfHeapReserve']
                      ] = pefile_info.OPTIONAL_HEADER.SizeOfHeapReserve
        except:
            LResource[Resources_header['Size:OfStackReserve']] = 0
            LResource[Resources_header['SizeOfStackCommit']] = 0
            LResource[Resources_header['SizeOfHeapReserve']] = 0

        LResource[Resources_header['SizeOfHeapCommit']
                  ] = pefile_info.OPTIONAL_HEADER.SizeOfHeapCommit
        LResource[Resources_header['LoaderFlags']
                  ] = pefile_info.OPTIONAL_HEADER.LoaderFlags
        LResource[Resources_header['NumberOfRvaAndSizes']
                  ] = pefile_info.OPTIONAL_HEADER.NumberOfRvaAndSizes

        entropy = []
        characteristics = []
        raw_sizes = []
        Misc_list = []

    # initialize  virtual address_list and raw sizes and entropy
    # check the suspeicous seections
        numSuS_Sections = 0
        for m in pefile_info.sections:
            entropy.append(m.get_entropy())
            characteristics.append(m.Characteristics)
            raw_sizes.append(m.SizeOfRawData)
            Misc_list.append(m.Misc)
            if ''.join(e.lower() for e in m.Name if str(e).isalpha()) not in ['rsrc', 'data', 'code', 'rdata']:
                numSuS_Sections += 1

        LResource[Resources_header['Num_Suspecious_Sections']] = numSuS_Sections

    # initialize Section

        LResource[Resources_header['SectionsMeanEntropy']] = sum(
            entropy) / float(len(entropy))
        LResource[Resources_header['SectionsMinEntropy']] = min(entropy)
        LResource[Resources_header['SectionsMaxEntropy']] = max(entropy)

    # initialize  Characteristics

        LResource[Resources_header['CharacteristicsMean']] = sum(
            characteristics)/float(len(characteristics))
        LResource[Resources_header['CharacteristicsMin']] = min(
            characteristics)
        LResource[Resources_header['CharacteristicsMax']] = max(
            characteristics)

    # initialize Misc
        LResource[Resources_header['MiscMean']] = sum(
            Misc_list)/float(len(Misc_list))
        LResource[Resources_header['MiscMin']] = min(Misc_list)
        LResource[Resources_header['MiscMax']] = max(Misc_list)
        try:
            # import
            LResource[Resources_header['ImportnumberofDLL']] = len(
                pefile_info.DIRECTORY_ENTRY_EXPORT.symbols)
    # export
            LResource[Resources_header['SymbolExportNumber']] = len(
                pefile_info.DIRECTORY_ENTRY_EXPORT.symbols)
        except:
            LResource[Resources_header['ImportnumberofDLL']] = 0
            LResource[Resources_header['SymbolExportNumber']] = 0
    # add md5 for  uniqueness
        try:
            LResource[Resources_header['md5']] = hashlib.md5(
                open(file_path).read()).hexdigest()
        except:
            LResource[Resources_header['md5']] = 0

    def EXTRACT_FILE_HEADER_INFO(self, LResource, Resources_header, file_path):
        pefile_info = pefile.PE(file_path)

        LResource[Resources_header['Machine']
                  ] = pefile_info.FILE_HEADER.Machine
        LResource[Resources_header['SizeOfOptionalHeader']
                  ] = pefile_info.FILE_HEADER.SizeOfOptionalHeader
        LResource[Resources_header['Characteristics']
                  ] = pefile_info.FILE_HEADER.Characteristics
        LResource[Resources_header['NumberofSections']
                  ] = pefile_info.FILE_HEADER.NumberOfSections

        try:
            LResource[Resources_header['TimeDateStamp']
                      ] = pefile_info.FILE_HEADER.TimeDateStamp
            LResource[Resources_header['PointerToSymbolTable']
                      ] = pefile_info.FILE_HEADER.PointerToSymbolTable
        except:
            LResource[Resources_header['TimeDateStamp']] = 0
            LResource[Resources_header['PointerToSymbolTable']] = 0

        LResource[Resources_header['NumberOfSymbols']
                  ] = pefile_info.FILE_HEADER.NumberOfSymbols

        #print( len(LResource))

    def EXTRACT_DIRECTORY_ENTRY_LOAD_CONFIG(self, LResource, Resources_header, file_path):
        pe = pefile.PE(file_path)

        try:
            LResource[Resources_header['Load_GlobalFlagsClear']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GlobalFlagsClear
            LResource[Resources_header['Load_GlobalFlagsSet']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GlobalFlagsSet
        except:
            LResource[Resources_header['Load_GlobalFlagsClear']] = 0
            LResource[Resources_header['Load_GlobalFlagsSet']] = 0

        try:
            LResource[Resources_header['Load_GlobalFlagsSet']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GlobalFlagsSet
            LResource[Resources_header['Load_CriticalSectionDefaultTimeout']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.CriticalSectionDefaultTimeout
            LResource[Resources_header['Load_DeCommitFreeBlockThreshold']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.DeCommitFreeBlockThreshold
        except:

            LResource[Resources_header['Load_GlobalFlagsSet']] = 0
            LResource[Resources_header['Load_CriticalSectionDefaultTimeout']] = 0
            LResource[Resources_header['Load_DeCommitFreeBlockThreshold']] = 0

        try:
            LResource[Resources_header['Load_DeCommitTotalFreeThreshold']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.DeCommitTotalFreeThreshold
            LResource[Resources_header['Load_LockPrefixTable']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.LockPrefixTable
            LResource[Resources_header['Load_VirtualMemoryThreshold']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.VirtualMemoryThreshold
        except:

            LResource[Resources_header['Load_DeCommitTotalFreeThreshold']] = 0
            LResource[Resources_header['Load_LockPrefixTable']] = 0
            LResource[Resources_header['Load_VirtualMemoryThreshold']] = 0

        try:
            LResource[Resources_header['Load_ProcessHeapFlags']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.ProcessHeapFlags
            LResource[Resources_header['Load_ProcessAffinityMask']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.ProcessAffinityMask
            LResource[Resources_header['Load_CSDVersion']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.CSDVersion

        except:
            LResource[Resources_header['Load_ProcessHeapFlags']] = 0
            LResource[Resources_header['Load_ProcessAffinityMask']] = 0
            LResource[Resources_header['Load_CSDVersion']] = 0

        try:
            LResource[Resources_header['Load_Reserved1']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.Reserved1
            LResource[Resources_header['Load_EditList']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.EditList
            LResource[Resources_header['Load_SecurityCookie']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SecurityCookie

        except:
            LResource[Resources_header['Load_Reserved1']] = 0
            LResource[Resources_header['Load_EditList']] = 0
            LResource[Resources_header['Load_SecurityCookie']] = 0

        try:
            LResource[Resources_header['Load_SEHandlerTable']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SEHandlerTable
            LResource[Resources_header['Load_SEHandlerCount']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.SEHandlerCount
            LResource[Resources_header['Load_GuardCFCheckFunctionPointer']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GuardCFCheckFunctionPointer

        except:
            LResource[Resources_header['Load_SEHandlerTable']] = 0
            LResource[Resources_header['Load_SEHandlerCount']] = 0
            LResource[Resources_header['Load_GuardCFCheckFunctionPointer']] = 0
        try:

            LResource[Resources_header['Load_Reserved2']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.Reserved2
            LResource[Resources_header['Load_GuardCFFunctionTable']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GuardCFFunctionTable
            LResource[Resources_header['Load_GuardCFFunctionCount']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GuardCFFunctionCount
            LResource[Resources_header['Load_GuardFlags']
                      ] = pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GuardFlags
        except:
            LResource[Resources_header['Load_Reserved2']] = 0
            LResource[Resources_header['Load_GuardCFFunctionTable']] = 0
            LResource[Resources_header['Load_GuardCFFunctionCount']] = 0
            LResource[Resources_header['Load_GuardFlags']] = 0

    def EXTRACT_DOS_HEADER(self, LResource, Resources_header, file_path):

        pefile_info = pefile.PE(file_path)
        try:
            LResource[Resources_header['e_magic']
                      ] = pefile_info.DOS_HEADER.e_magic
            LResource[Resources_header['e_cblp']
                      ] = pefile_info.DOS_HEADER.e_cblp
            LResource[Resources_header['e_cp']] = pefile_info.DOS_HEADER.e_cp
        except:
            LResource[Resources_header['e_magic']] = 0
            LResource[Resources_header['e_cblp']] = 0
            LResource[Resources_header['e_cp']] = 0
        try:
            LResource[Resources_header['e_crlc']
                      ] = pefile_info.DOS_HEADER.e_crlc
            LResource[Resources_header['e_cparhdr']
                      ] = pefile_info.DOS_HEADER.e_cparhdr
            LResource[Resources_header['e_minalloc']
                      ] = pefile_info.DOS_HEADER.e_minalloc
        except:
            LResource[Resources_header['e_crlc']] = 0
            LResource[Resources_header['e_cparhdr']] = 0
            LResource[Resources_header['e_minalloc']] = 0
        try:
            LResource[Resources_header['e_maxalloc']
                      ] = pefile_info.DOS_HEADER.e_maxalloc
            LResource[Resources_header['e_ss']] = pefile_info.DOS_HEADER.e_ss
            LResource[Resources_header['e_sp']] = pefile_info.DOS_HEADER.e_sp
        except:
            LResource[Resources_header['e_maxalloc']] = 0
            LResource[Resources_header['e_ss']] = 0
            LResource[Resources_header['e_sp']] = 0
        try:
            LResource[Resources_header['e_csum']
                      ] = pefile_info.DOS_HEADER.e_csum
            LResource[Resources_header['e_ip']] = pefile_info.DOS_HEADER.e_ip
            LResource[Resources_header['e_cs']] = pefile_info.DOS_HEADER.e_cs
        except:
            LResource[Resources_header['e_csum']] = 0
            LResource[Resources_header['e_ip']] = 0
            LResource[Resources_header['e_cs']] = 0
        try:
            LResource[Resources_header['e_lfarlc']
                      ] = pefile_info.DOS_HEADER.e_lfarlc
            LResource[Resources_header['e_ovno']
                      ] = pefile_info.DOS_HEADER.e_ovno
            LResource[Resources_header['e_res']] = len(
                pefile_info.DOS_HEADER.e_res)
        except:
            LResource[Resources_header['e_lfarlc']] = 0
            LResource[Resources_header['e_ovno']] = 0
            LResource[Resources_header['e_res']] = 0
        try:
            LResource[Resources_header['e_oemid']
                      ] = pefile_info.DOS_HEADER.e_oemid
            LResource[Resources_header['e_oeminfo']
                      ] = pefile_info.DOS_HEADER.e_oeminfo
            LResource[Resources_header['e_res2']] = len(
                pefile_info.DOS_HEADER.e_res2)
            LResource[Resources_header['e_lfanew']
                      ] = pefile_info.DOS_HEADER.e_lfanew
        except:
            LResource[Resources_header['e_oemid']] = 0
            LResource[Resources_header['e_oeminfo']] = 0
            LResource[Resources_header['e_res2']] = 0
            LResource[Resources_header['e_lfanew']] = 0

    def EXTRACT_DIRECTORY_ENTRY_RESOURCE(self, LResource, Resources_header, file_path):

        #ext_dir_entry_res =['Characteristics','TimeDateStamp','NumberOfNamedEntries','NumberOfIdEntries','','','','','','']
        pefile_info = pefile.PE(file_path)

        #print ("pefile info is this: ",pefile_info)

        try:
            LResource[Resources_header['Directory_Characteristics']
                      ] = pefile_info.DIRECTORY_ENTRY_RESOURCE.struct.Characteristics
        except:
            LResource[Resources_header['Directory_Characteristics']] = 0

        try:
            LResource[Resources_header['Directory_TimeDateStamp']
                      ] = pefile_info.DIRECTORY_ENTRY_RESOURCE.struct.TimeDateStamp

        except:
            LResource[Resources_header['Directory_TimeDateStamp']] = 0

        try:
            LResource[Resources_header['Directory_NumberOfNamedEntries']
                      ] = pefile_info.DIRECTORY_ENTRY_RESOURCE.struct.NumberOfNamedEntries
        except:
            LResource[Resources_header['Directory_NumberOfNamedEntries']] = 0

        try:
            LResource[Resources_header['Directory_NumberOfIdEntries']
                      ] = pefile_info.DIRECTORY_ENTRY_RESOURCE.struct.NumberOfIdEntries
        except:
            LResource[Resources_header['Directory_NumberOfIdEntries']] = 0

    def All_Resources(self, filepath, fileName):
        LResource = {}
        Resources_header = {}
        file_path = self.base_path + "scripts/etl/staticfeature.txt"
        stop = sum(1 for line in open(file_path))
        feature = open(file_path, "r", encoding="utf-8")
        for ind in itertools.islice(feature, stop):
            fields = ind.split(':', 1)
            Resources_header[fields[1].strip()] = fields[0]
        feature.close()

        self.EXTRACT_DIRECTORY_ENTRY_RESOURCE(
            LResource, Resources_header, filepath)
        self.EXTRACT_DOS_HEADER(LResource, Resources_header, filepath)
        self.EXTRACT_DIRECTORY_ENTRY_LOAD_CONFIG(
            LResource, Resources_header, filepath)
        self.EXTRACT_FILE_HEADER_INFO(LResource, Resources_header, filepath)
        self.EXTRACT_OPTIONAL_HEADER_INFO(
            LResource, Resources_header, filepath, fileName)

        # join value of one dict to key of another dict
        #d1 = {v: k for k, v in Resources_header.items()}
        # print(d1)

        # print(len(Resources_header))
        LResource['2'] = 0

        dict3 = {k: LResource[v] for k, v in Resources_header.items()}
        # delete a key with 'Malicious'
        del dict3['Malicious']
        return dict3

    def get_sf_dict(self):
        return self.All_Resources(self.filepath, self.filename)


if __name__ == "__main__":
    pass
