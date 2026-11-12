# DefinedFlow

Public educational code and Jupyter notebooks about structured products.

## Examples

| Example | Notebook | Python source |
| --- | --- | --- |
| A maturity payoff, in Python | [Open notebook](notebooks/maturity-payoff/maturity_payoff.ipynb) | [Open script](notebooks/maturity-payoff/participation_payoff.py) |

Each example lives in its own folder with its notebook, supporting code, and numerical checks.

## Run the maturity-payoff example

Use Python 3.11+. The example and its tests use only the Python standard library; there are no market-data downloads or API keys.

Clone this repository and enter the example folder:

```bash
git clone https://github.com/maximus-POL/DefinedFlow.git
cd DefinedFlow/notebooks/maturity-payoff
```

Open `maturity_payoff.ipynb` in JupyterLab or a notebook-capable editor with a Python kernel. Keep the adjacent `participation_payoff.py` file in place, use this example folder as the kernel working directory, and restart the kernel and run all cells from the beginning. The saved notebook includes executed example outputs for reading on GitHub.

To run the Python script directly:

```bash
python3 participation_payoff.py 1000 100 120 0.8
```

Expected output: `1160.00` illustrative currency units, including principal.

Run the numerical and notebook-output checks:

```bash
python3 -B test_participation_payoff.py
```

The notebook explains the hypothetical terms, input units, rounding, limitations, and financial sources. It calculates a conditional maturity payment; it does not estimate a product's price or make an investment recommendation.
