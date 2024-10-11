import re


# TODO: this should be more compatible for https://peps.python.org/pep-0508/
def transform_module_name(input_str):
    match = re.match(r"([a-zA-Z0-9_\-\[\]]+)", input_str)
    if match:
        module_name = match.group(1).strip()

        version_names = input_str[len(module_name):].strip().strip("()")
        version_constraint = version_names.split(",")
        package_name = "python3-" + module_name
        if len(version_constraint) > 1:
            constraints_string = " with ".join([
                f"{package_name}{constraint}" for constraint in version_constraint
            ])
            result_string = f"({constraints_string})"
        else:
            result_string = f"({package_name}{version_constraint[0]})"
    else:
        result_string = "Invalid input format"

    return result_string


def refine_requires(req: str) -> str:
    """
    return only requires without ';' (thus no extra)
    """
    ra = req.split(";", 1)
    # Do not add requires which has ;, which is often has very complicated precondition
    return transform_module_name(ra[0])
