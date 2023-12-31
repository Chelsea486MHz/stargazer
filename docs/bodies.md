![](./logo.png)

# Stargazer bodies

All Stargazer computations occur on Stargazer bodies. A Stargazer body can be defined with the following object:

```
{
    "position": {
        "x": x,
        "y": y,
        "z": z
    },
    "velocity": {
        "x": x,
        "y": y,
        "z": z
    },
    "acceleration": {
        "x": x,
        "y": y,
        "z": z
    },
    "force": {
        "x": x,
        "y": y,
        "z": z
    },
    "value": {
        "mass": mass,
        "electrostatic_charge": electrostatic_charge
    }
}
```

The `position`, `velocity`, `acceleration`, and `force` variables refer to the cartesian coordinates of their corresponding vectors in 3D space.

The variables in the `value` array are used in some computations.

All values are unitless integers.