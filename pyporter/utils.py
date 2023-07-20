import re

# def transform_module_name(s: str) -> str:
#     """
#     return module name with version restriction.
#     Any string with '.' or '/' is considered file, and will be ignored
#     Modules start with python- will be changed to python3- for consistency.
#     """
#     ns = re.split("[()]", s)
#     ver_constrain = []
#     ns[0] = ns[0].strip()
#     if ns[0].startswith("python-"):
#         ns[0] = ns[0].replace("python-", "python3-")
#     else:
#         ns[0] = "python3-" + ns[0]

# # Process version constraints
#     if len(ns) > 1:
#         ver_constrain.append(ns[1])

#     if len(ver_constrain) > 0:
#         return f"({ns[0]} {ver_constrain[0]})"
#     else:
#         return ns[0]


def transform_module_name(input_str):
    # Extracting the module name from the input string
    module_name = re.match(r"([a-zA-Z0-9_-]+)", input_str).group(1)
    version_names = input_str[len(module_name):]
    # Extracting the version constraint from the input string
    version_constraint = version_names.split(",")
    package_name = "python3-" + module_name
    if len(version_constraint) > 1:
        constraints_string = " with ".join([
            f"{package_name}{constraint}" for constraint in version_constraint
        ])
        result_string = f"({constraints_string})"
    else:
        result_string = f"({package_name}{version_constraint[0]})"

    return result_string


def refine_requires(req: str) -> str:
    """
    return only requires without ';' (thus no extra)
    """
    ra = req.split(";", 1)
    # Do not add requires which has ;, which is often has very complicated precondition
    return transform_module_name(ra[0])
