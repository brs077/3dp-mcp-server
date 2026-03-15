# get-model-code

Retrieve the build123d source code used to create a model.

## When to use

Use when the user wants to see, review, or modify the code that generated a model.

## Instructions

1. Call `get_model_code` with the model name
2. Present the code to the user
3. If they want modifications, use `create_model` with updated code

## Parameters

- `name` (required): Name of the model

## Example

```
get_model_code(name="bracket")
```
