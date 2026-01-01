import hget
import os
import shutil

def test_library():
    # Clean up previous tests
    for d in ["lib_test1", "lib_test2"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            
    items = [
        ["https://raw.githubusercontent.com/google/guava/master/README.md", "lib_test1"],
        {"url": "https://raw.githubusercontent.com/google/guava/master/CONTRIBUTING.md", "dir": "lib_test2", "out": "CONTRIB.md"}
    ]
    
    print("Starting library download...")
    hget.download(items)
    
    # Verify
    assert os.path.exists("lib_test1/README.md")
    assert os.path.exists("lib_test2/CONTRIB.md")
    print("Library verification successful!")

if __name__ == "__main__":
    test_library()
