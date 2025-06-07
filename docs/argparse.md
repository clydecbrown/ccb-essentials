# argparse.py

`str2bool` is a helper function which implements a missing boolean type for `argparse`. This allows flexible inputs for boolean values on the command line.

- **Boolean CLI inputs**: Handle truthy and falsy inputs to a Python script, with type checking.

The function checks the input string against a set of predefined values that represent `True` or `False`. The inputs are not case sensitive. All other inputs raise `ArgumentTypeError`.

## Predefined Values

- **Truthy**: `'1', 'true', 't', 'yes', 'y'`
- **Falsy**: `'0', 'false', 'f', 'no', 'n'`

## Example Usage

*python*

```python
parser = argparse.ArgumentParser(description="Example usage of str2bool.")
parser.add_argument('flag', type=str2bool, help="A boolean flag.")
args = parser.parse_args()
print(type(args.flag), args.flag)  # <class 'bool'> True
                                   #  or
                                   # <class 'bool'> False
```
