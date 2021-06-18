import ujson

class Description:
    def __init__(self,
                data_path: str,
                content: dict) -> None:
                
        self.file_address = f'{data_path}file_description.jsonl'
        self.content = content

    def persist(self):
        with open(self.file_address, "a+") as f:
            f.write(ujson.dumps(self.content) + '\n')