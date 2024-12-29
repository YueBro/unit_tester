import pickle as pkl
import gzip
import base64


def serialize(var) -> str:
    return base64.b64encode(gzip.compress(pkl.dumps(var))).decode("ascii")


def unserialize(s: str):
    return pkl.loads(gzip.decompress(base64.b64decode(s)))
