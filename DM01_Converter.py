#This code is use to read in full CAN messages and output only the decomposed DM01 contents
#Created by Ian Tempelemeyer 1/11/2025 
#Multiple debug serial prints commented out by "##"
#Needs to be verified...

#! Does not seem to work for FECA messages with more than one DTC
#! DTC are 4 byte strings, Suceeding the first 5 bits.
#! Need to be redun to include lamp status and SPN1,2,3,4,5...

import re

# Example log data
can_log = [
    "18FECA00 00 00 01 02 E3 00 19 07 E3 00 19 07 E3 00 19 07 04",
    "18FECA03 01 00 02 04 A2 00 24 03",
    "18FECB07 01 00 02 04 A2 00 24 03",
    "18FEBB08 01 00 02 04 A2 00 24 03",
    "18FEBB04 01 00 02 04 A2 00 24 03",
    "18FEBB05 01 00 02 04 A2 00 24 03",
]

def parse_dm01_message(data):
    results = []
    for message in data:
        #print(f"Processing: {message}")
        
        # Extract CAN ID and payload
        match = re.match(r"^([0-9A-Fa-f]{8})\s+(.*)", message)
        if not match:
            print("No match for CAN ID and payload format.")
            continue
        
        can_id = match.group(1)
        payload = match.group(2)
        
        # Check if the PGN matches DM01 (PGN 0xFECA)
        pgn = (int(can_id, 16) >> 8) & 0xFFFF
        ##print(f"Extracted PGN: {hex(pgn)}, SA: {can_id[-2:]}")
        
        if pgn != 0xFECA:
            ##print("Not a DM01 message.")
            continue
        
        # Extract SA
        sa = int(can_id[-2:], 16)
        
        # Convert payload to bytes
        raw_bytes = [int(b, 16) for b in payload.split()]
        ##print(f"Raw bytes: {list(enumerate(raw_bytes))}")  # Debug: Show indexed payload bytes
        
        if len(raw_bytes) < 5:  # Ensure enough data for a DM01 message
            print("Payload too short for DM01.")
            continue
        
        # Parse each DTC (3 bytes per DTC)
        dtc_data = raw_bytes[5:]  # Skip first 5 bytes (status bytes)
        ##print(f"DTC bytes: {list(enumerate(dtc_data))}")  # Debug: Show indexed DTC bytes
        
        for i in range(0, len(dtc_data), 3):
            if i + 2 >= len(dtc_data):
                print(f"Incomplete DTC data at index {i}, skipping.")
                break
            spn = (dtc_data[i + 1] << 8) | dtc_data[i]  # SPN encoded in first 2 bytes
            fmi = dtc_data[i + 2] & 0x1F  # FMI in lower 5 bits of third byte
            oc = (dtc_data[i + 2] >> 5) & 0x07  # Upper 3 bits for Occurrence Count
            #print(f"Decoded DTC - SPN: {spn}, FMI: {fmi}, OC: {oc}")  # Debug
            results.append({"SA": sa, "SPN": spn, "FMI": fmi, "OC": oc})
    return results

# Parse the log data
parsed_data = parse_dm01_message(can_log)

# Print the parsed results
if parsed_data:
    for dtc in parsed_data:
        print(f"SA: {dtc['SA']}, SPN: {dtc['SPN']}, FMI: {dtc['FMI']}, OC: {dtc['OC']}")
else:
    print("No DM01 messages found.")
