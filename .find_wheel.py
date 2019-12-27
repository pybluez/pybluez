import glob
import os

path = next(glob.iglob("dist/*.whl"))
print("::set-output name=whl_file::" + path)
print("::set-output name=whl_name::" + os.path.basename(path))
