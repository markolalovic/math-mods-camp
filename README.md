# math-mods-camp

## How-to

### Dependencies

* Python 3
* `numpy`
* `matplotlib` for drawing
* `pandas` - only for showing the results in dataframes

### Evaluation
To evaluate a layout, run from `src` directory `python3 run.py path-to-the-layout-file.json`, for example:
```bash
$ python3 run.py "../data/layouts/parabolic-layout.json"
> 233.00694655878540429
```

See also `Hypothetical-Plant.ipynb` notebook in `notebooks` directory.

## Evaluation results

Below are the current results for a few basic layouts evaluated on the Hypothetical Plant:

|         Layout         |    Energy  |
|-------------------------|---------------|
| theater-layout | 243.62 |
| parabolic-layout | 233.01 |
| grid-layout-2 | 194.62 |
| grid-layout | 178.95 |
| parabolic-layout-flipped | 157.35 |
| uniform-random-layout | 118.18 |
