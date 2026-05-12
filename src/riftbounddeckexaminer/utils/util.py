from collections import defaultdict
import sys


def get_user_input[T](
    options: dict[str, T],
    prompt: str = "",
    multiselect: bool = False,
    sort_options=True,
) -> dict[str, T]:
    """
    Options should be a key-value pair consisting of the name of the object and the
    object iself. Prompt (optional) is printed before the choices in numerical order.

    Returns the name and the selected object or objects if multiselect is enabled.
    """
    sorted_options = options.keys()
    if sort_options:
        sorted_options = sorted(options.keys())

    numbered_options = defaultdict()

    for idx, option in enumerate(sorted_options):
        numbered_options[idx + 1] = option

    retry = False
    selections = defaultdict()
    while True:
        option_list = [""]

        if retry:
            option_list.append("Invalid input, retry:")

        option_list.append(prompt)

        if multiselect:
            for opt_key, opt_val in numbered_options.items():
                if opt_val in selections:
                    option_list.append(f"*{opt_key}. {opt_val}")
                else:
                    option_list.append(f" {opt_key}. {opt_val}")
        else:
            for option_key, option_val in numbered_options.items():
                option_list.append(f" {option_key}. {option_val}")

        full_prompt = "\n".join(option_list) + "\n"

        print(full_prompt)
        sys.stdout.flush()
        user_choice = input()

        if user_choice.isdigit() and int(user_choice) in numbered_options:
            if multiselect:
                selections[numbered_options[int(user_choice)]] = options[
                    numbered_options[int(user_choice)]
                ]
                # select again
                continue
            else:
                return {
                    numbered_options[int(user_choice)]: options[
                        numbered_options[int(user_choice)]
                    ]
                }
        elif multiselect and not user_choice:
            return selections
        retry = True


def get_user_input_freeform_int(
    default: int, max: int, min: int = 0, prompt: str = ""
) -> int:
    """
    Get an integer value from user input. Includes default, min, and max in the prompt automatically.
    Example:

    {prompt}
    Min: 0 Max: 10 [default: 10 (enter to continue)]
    """
    retry = False
    while True:
        prompts = [""]
        if retry:
            prompts.append("Invalid input, retry:")
        prompts.append(prompt)
        prompts.append(
            f"Min: {min} Max: {max} [default: {default} (enter to continue)]"
        )
        full_prompt = "\n".join(prompts) + "\n"
        print(full_prompt)
        user_choice = input()

        if not user_choice:
            print(f"Selected default value of {default}.")
            return default
        elif user_choice.isdigit():
            amount = int(user_choice)
            if amount <= max and amount >= min:
                return amount

        retry = True


def unpack_single_dict_entry[T](single: dict[str, T]) -> tuple[str, T]:
    return next(iter(single.items()))
