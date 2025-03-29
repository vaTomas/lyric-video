from typing import Optional


def string_content_check(
        input_string: str,
        starts_with: Optional[str] = None,
        contains: Optional[str] = None,
        ends_with: Optional[str] = None,
        match_case: bool = False,
        must_pass_all: bool = False # AND operation
) -> bool:
    """
    Checks if a given string matches the filtering criteria.

    Args:
        input_string (str): The string to check.
        starts_with (str, optional): String must start with this string.
        contains (str, optional): String must contain this substring.
        ends_with (str, optional): String must end with this string.
        match_case (bool): Whether the match is case-sensitive.
        must_pass_all (bool): If True, all criteria must match; otherwise, any match is sufficient.

    Returns:
        bool: True if the string matches the criteria, False otherwise.
    """
    if input_string is not None and not isinstance(input_string, str):
        raise TypeError(f"input_string type expected None or str: got {type(input_string)}") 
    
    if starts_with is not None and not isinstance(starts_with, str):
        raise TypeError(f"input_string type expected None or str: got {type(starts_with)}") 
    
    if contains is not None and not isinstance(contains, str):
        raise TypeError(f"input_string type expected None or str: got {type(contains)}") 
    
    if ends_with is not None and not isinstance(ends_with, str):
        raise TypeError(f"input_string type expected None or str: got {type(ends_with)}") 
    
    if match_case is not None and not isinstance(match_case, bool):
        raise TypeError(f"input_string type expected bool: got {type(match_case)}") 
    
    if must_pass_all is not None and not isinstance(must_pass_all, bool):
        raise TypeError(f"input_string type expected bool: got {type(must_pass_all)}") 
    


    if not match_case:
        input_string = input_string.lower()
        starts_with = starts_with.lower() if starts_with else None
        contains = contains.lower() if contains else None
        ends_with = ends_with.lower() if ends_with else None

    checks = set()

    
    if starts_with:
        checks.add(input_string.startswith(starts_with))

    if contains:
        checks.add(contains in input_string)

    if ends_with:
        checks.add(input_string.endswith(ends_with))

    if must_pass_all:
        return all(checks)

    return any(checks) if checks else True


def main():
    input_string = 'aAaadad.$@%@#.bBb.13131324151314.cCc'

    print("Test Start Pass")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aaa'
    )
    print(result == True)

    print("Test Start Fail")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'bbb'
    )
    print(result == False)
    
    print("Test Contain Pass")
    result = string_content_check(
        input_string = input_string,
        contains = 'bbb'
    )
    print(result == True)
    
    print("Test Contain Fail")
    result = string_content_check(
        input_string = input_string,
        contains = 'ddd'
    )
    print(result == False)
    
    print("Test End Pass")
    result = string_content_check(
        input_string = input_string,
        ends_with = 'ccc'
    )
    print(result == True)
    
    print("Test End Fail")
    result = string_content_check(
        input_string = input_string,
        ends_with = 'aaa'
    )
    print(result == False)
    
    print("Test Match Case Pass")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aAa',
        must_pass_all = True
    )
    print(result == True)

    print("Test Match Case Fail")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aaa',
        must_pass_all = True
    )
    print(result == True)

    print("Test Match Case Pass")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aaa',
        contains = 'bbb',
        ends_with = 'ccc',
        must_pass_all = True
    )
    print(result == True)

    print("Test Check Any Pass")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aaa',
        contains = 'bbb',
        ends_with = 'ccc'
    )
    print(result == True)

    print("Test Check Any Fail")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'ccc',
        contains = 'ddd',
        ends_with = 'aaa'
    )
    print(result == False)
    
    print("Test Check All Pass")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aaa',
        contains = 'bbb',
        ends_with = 'ccc',
        must_pass_all = True
    )
    print(result == True)

    print("Test Check All Fail")
    result = string_content_check(
        input_string = input_string,
        starts_with = 'aaa',
        contains = 'ddd',
        ends_with = 'bbb',
        must_pass_all = True
    )
    print(result == False)
    

if __name__ == "__main__":
    main()