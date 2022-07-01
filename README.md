# math-mods-camp

## How-to

### Dependencies

* Python 3
* `numpy`
* `matplotlib` for drawing
* `pandas` - only for showing the results in dataframes

### Evaluation
To evaluate a layout, see `run.py` script in [`src`](https://github.com/markolalovic/math-mods-camp/tree/main/src) directory, and execute `python3 run.py`.

See also [`Toy-Model.ipynb`](https://github.com/markolalovic/math-mods-camp/blob/main/notebooks/Toy-Model.ipynb) notebook in [`notebooks`](https://github.com/markolalovic/math-mods-camp/tree/main/notebooks) directory.

### Files
To create a new layout for evaluation and testing using the Tiny Plant, you have to write a list of `n=5` heliostat coordinates `[xi, yi]` in the following format:

`[[x1, y1], [x2, y2], ..., [xn, yn]]`

and save it as `name-of-layout.json` to `data/layouts` directory.

For the layout to be valid, the coordinates have to be in the Tiny Plants field area:
```
0 <= xi <= 35
0 <= yi <= 10
```

Heliostats must not be too close, they have to be at least 2 times the radius of a bounding circle appart, this distance is equal to heliostat size:

```
|(xi, yi) - (xj, yj)| >= 4
```

And heliostats must not be too close to the receiver
```
|(xi, yi) - (0, 12)| >= 4
```

See the existing layouts in [`data/layouts`](https://github.com/markolalovic/math-mods-camp/tree/main/data/layouts), for example: [grid-layout.json](https://raw.githubusercontent.com/markolalovic/math-mods-camp/main/data/layouts/grid-layout.json) with coordinates for 5 heliostats.

## Evaluation results

Below are the current results for a few basic layouts evaluated on the Tiny plant:

|         Layout         |    Energy  |
|-------------------------|---------------|
| parabolic-layout | 63.14 |
| theater-layout   | 60.64 |
| grid-layout | 48.22 |
| tiny-layout | 45.19 |
| uniform-random-layout | 34.75 (7.24) |
