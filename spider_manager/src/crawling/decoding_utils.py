# Functions dealing with byte-to-str conversions

def decode_binary_entry(data):
    if type(data) == list:
        return list(map(decode_binary_entry, data))
    elif type(data) == dict:
        result = {}

        for entry_key in data:
            decoded_key = entry_key

            if type(entry_key) == bytes:
                decoded_key = entry_key.decode('utf-8')

            result[decoded_key] = decode_binary_entry(data[entry_key])

        return result
    elif type(data) == bytes:
        return data.decode('utf-8')
    else:
        return data
