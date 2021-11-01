import os
import ujson


class Description:
    def __init__(self,
                description_path: str,
                content: dict) -> None:
        self.file_address = os.path.join(description_path, 'file_description.jsonl')
        self.content = content

    def persist(self):
        with open(self.file_address, "a+") as f:
            f.write(ujson.dumps(self.content) + '\n')
