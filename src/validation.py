def validate(package: str) -> bool:
    PACKAGES: list[str] = ["cpp-cloc", "pdf-toolkit"]
    if package in PACKAGES:
        return True
    return False
