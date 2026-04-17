from hashlib import sha256


def get_sha256(file: str) -> str:
    hash_object = sha256()
    with open(file, "rb") as f:
        while chunk := f.read(4096):
            hash_object.update(chunk)

    return hash_object.hexdigest()
