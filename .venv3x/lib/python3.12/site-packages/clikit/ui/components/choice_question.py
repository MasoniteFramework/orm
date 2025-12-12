import os
import re

from .question import Question


class SelectChoiceValidator:
    def __init__(self, question):
        """
        Constructor.
        """
        self._question = question
        self._values = question.choices

    def validate(self, selected):
        """
        Validate a choice.
        """
        # Collapse all spaces.
        if isinstance(selected, int):
            selected = str(selected)

        selected_choices = selected.replace(" ", "")

        if self._question.supports_multiple_choices():
            # Check for a separated comma values
            if not re.match("^[a-zA-Z0-9_-]+(?:,[a-zA-Z0-9_-]+)*$", selected_choices):
                raise ValueError(self._question.error_message.format(selected))

            selected_choices = selected_choices.split(",")
        else:
            selected_choices = [selected]

        multiselect_choices = []
        for value in selected_choices:
            results = []

            for key, choice in enumerate(self._values):
                if choice == value:
                    results.append(key)

            if len(results) > 1:
                raise ValueError(
                    "The provided answer is ambiguous. Value should be one of {}.".format(
                        " or ".join(str(r) for r in results)
                    )
                )

            try:
                result = self._values.index(value)
                result = self._values[result]
            except ValueError:
                try:
                    value = int(value)

                    if 0 <= value < len(self._values):
                        result = self._values[value]
                    else:
                        result = False
                except ValueError:
                    result = False

            if result is False:
                raise ValueError(self._question.error_message.format(value))

            multiselect_choices.append(result)

        if self._question.supports_multiple_choices():
            return multiselect_choices

        return multiselect_choices[0]


class ChoiceQuestion(Question):
    """
    Multiple choice question.
    """

    def __init__(self, question, choices, default=None):
        super(ChoiceQuestion, self).__init__(question, default)

        self._multi_select = False
        self._choices = choices
        self._validator = SelectChoiceValidator(self).validate
        self._autocomplete_values = choices
        self._prompt = " > "
        self._error_message = 'Value "{}" is invalid'

    @property
    def error_message(self):
        return self._error_message

    @property
    def choices(self):
        return self._choices

    def supports_multiple_choices(self):
        return self._multi_select

    def set_multi_select(self, multi_select):
        self._multi_select = multi_select

    def set_error_message(self, message):
        self._error_message = message

    def _write_prompt(self, io):
        """
        Outputs the question prompt.
        """
        message = self._question
        default = self._default

        if default is None:
            message = "<question>{}</>: ".format(message)
        elif self._multi_select:
            choices = self._choices
            default = default.split(",")

            for i, value in enumerate(default):
                default[i] = choices[int(value.strip())]

            message = "<question>{}</> [<comment>{}</>]:".format(
                message, ", ".join(default)
            )
        else:
            choices = self._choices
            message = "<question>{}</question> [<comment>{}</>]:".format(
                message, choices[int(default)]
            )

        if len(self._choices) > 1:
            width = max(*map(len, [str(k) for k, _ in enumerate(self._choices)]))
        else:
            width = 1

        messages = [message]
        for key, value in enumerate(self._choices):
            messages.append(" [<comment>{:{}}</>] {}".format(key, width, value))

        io.error_line("\n".join(messages))

        message = self._prompt

        io.error(message)
