
import importlib


def test_CleanupAction():
    imported_lib = importlib.import_module(f"lib.publish.apt-ftparchive")

    options = {
        "default_target": "test_repo/",
        "only_keep_version": 12
    }

    meta = {
        "name": "balmbooking-application",
        "dist": ".",
        "arch": "amd64"
    }

    step = imported_lib.BuildStep("abcd_test", options, meta)

    print(step.base_target)

    step.cleanupAction()


if __name__ == "__main__":
    test_CleanupAction()
