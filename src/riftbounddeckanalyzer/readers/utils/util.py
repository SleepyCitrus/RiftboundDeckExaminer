from collections import defaultdict


def get_user_input[T](
    options: dict[str, T], prompt: str = "", multiselect: bool = False
) -> dict[str, T]:
    """
    Options should be a key-value pair consisting of the name of the object and the
    object iself. Prompt (optional) is printed before the choices in numerical order.

    Returns the name and the selected object or objects if multiselect is enabled.
    """
    numbered_options = defaultdict()

    for idx, (key, value) in enumerate(options.items()):
        numbered_options[idx + 1] = key

    retry = False
    selections = defaultdict()
    while True:
        option_list = [""]
        if multiselect:
            for opt_key, opt_val in numbered_options.items():
                if opt_val in selections:
                    option_list.append(f"*{opt_key}. {opt_val}")
                else:
                    option_list.append(f" {opt_key}. {opt_val}")
        else:
            for option_key, option_val in numbered_options.items():
                option_list.append(f" {option_key}. {option_val}")

        full_prompt = prompt + "\n".join(option_list) + "\n"
        if retry:
            full_prompt = "\nInvalid input, retry:\n" + full_prompt

        user_choice = input(full_prompt)

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
        else:
            if multiselect and selections:
                return selections
            retry = True
