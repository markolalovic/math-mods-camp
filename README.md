# math-mods-camp

## How-to

### Dependencies

* Python 3
* `numpy`
* `matplotlib` for drawing
* `pandas` - only for showing the results in dataframes

### Evaluation
To evaluate a layout, run from [`src`](https://github.com/markolalovic/math-mods-camp/tree/main/src) directory `python3 run.py path-to-the-layout-file.json`, for example:
```bash
$ python3 run.py "../data/layouts/parabolic-layout.json"
> 233.00694655878540429
```

See also [`Hypothetical-Plant.ipynb`](https://github.com/markolalovic/math-mods-camp/blob/main/notebooks/Hypothetical-Plant.ipynb) notebook in [`notebooks`](https://github.com/markolalovic/math-mods-camp/tree/main/notebooks) directory.

### Files
To create a new layout for evaluation and testing using the Hypothetical Plant, you have to write the name and list of `n=20` heliostat coordinates `[xi, yi]` in the following format:

`{"name-of-layout": [[x1, y1], [x2, y2], ..., [xn, yn]]}`

and save it as `name-of-layout.json` to `data/layouts` directory. For the layout to be valid, the coordinates have to be in the Hypothetical Plants field area and must not be too close: 

```
0 <= xi <= 100
0 <= yi <= 20
|(xi, yi) - (xj, yj)| >= 3
```

See the existing layouts in [`data/layouts`](https://github.com/markolalovic/math-mods-camp/tree/main/data/layouts), for example: [grid-layout.json](https://raw.githubusercontent.com/markolalovic/math-mods-camp/main/data/layouts/grid-layout.json) with coordinates for 20 heliostats.

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
