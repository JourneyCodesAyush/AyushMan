def validate(package: str) -> bool:
    PACKAGES: list[str] = ["cpp-cloc", "c-utils", "pdf-toolkit"]
    if package in PACKAGES:
        return True
    return False
